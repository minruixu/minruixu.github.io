#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import io
import json
import re
import textwrap
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz
import requests
import yaml
from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS_DIR = ROOT / "_publications"
IMAGES_DIR = ROOT / "images" / "publications"
TEMP_DIR = Path("/tmp/codex_publication_enrichment")

ARXIV_ABS_PREFIX = "https://arxiv.org/abs/"
ARXIV_PDF_PREFIX = "https://arxiv.org/pdf/"
ARXIV_SEARCH_URL = "https://export.arxiv.org/api/query"
CROSSREF_URL = "https://api.crossref.org/works"
OPENALEX_WORKS_URL = "https://api.openalex.org/works"

ENRICHMENT_KEYS = {
    "abstract_text",
    "abstract_source_url",
    "abstract_source_label",
    "arxiv_id",
    "featured_figure",
    "featured_figure_caption",
    "featured_figure_source_url",
}

ARXIV_TITLE_OVERRIDES = {
    "Wireless edge-empowered metaverse: A learning-based incentive mechanism for virtual reality": "2111.03776",
    "Resource allocation in quantum key distribution (qkd) for space-air-ground integrated networks": "2208.08009",
    "Privacy-preserving intelligent resource allocation for federated edge learning in quantum internet": "2210.04308",
    "Quantum-secured space-air-ground integrated networks: Concept, framework, and case study": "2204.08673",
    "Secure and reliable transfer learning framework for 6g-enabled internet of vehicles": "2111.05804",
    "Sustainable aigc workload scheduling of geo-distributed data centers: A multi-agent reinforcement learning approach": "2304.07948",
    "Learning-based incentive mechanism for task freshness-aware vehicular twin migration": "2309.04929",
    "Joint foundation model caching and inference of generative ai services for edge intelligence": "2305.12130",
    "Generative ai-empowered effective physical-virtual synchronization in the vehicular metaverse": "2301.07636",
    "Learning-based sustainable multi-user computation offloading for mobile edge-quantum computing": "2211.06681",
    "Entangled pair resource allocation under uncertain fidelity requirements": "2304.04425",
    "Adaptive resource allocation in quantum key distribution (qkd) for federated learning": "2208.11270",
    "Stochastic qubit resource allocation for quantum cloud computing": "2210.12343",
    "A learning-based incentive mechanism for mobile aigc service in decentralized internet of vehicles": "2403.20151",
    "When quantum information technologies meet blockchain in web 3.0": "2211.15941",
    "Generative ai-empowered simulation for autonomous driving in vehicular mixed reality metaverses": "2302.08418",
    "A full dive into realizing the edge-enabled metaverse: Visions, enabling technologies, and challenges": "2203.05471",
    "Cooperative resource management in quantum key distribution (qkd) networks for semantic communication": "2209.11957",
    "Ai-generated network design: A diffusion model-based learning approach": "2303.13869",
    "Decentralized multimedia data sharing in iov: A learning-based equilibrium of supply and demand": "2403.20218",
    "When large language model agents meet 6g networks: Perception, grounding, and alignment": "2401.07764",
}

PUBLISHER_LABELS = {
    "arxiv.org": "arXiv",
    "ieeexplore.ieee.org": "IEEE Xplore",
    "dl.acm.org": "ACM Digital Library",
    "link.springer.com": "Springer",
    "springer.com": "Springer",
    "mdpi.com": "MDPI",
    "www.mdpi.com": "MDPI",
    "academic.oup.com": "Oxford Academic",
    "onlinelibrary.wiley.com": "Wiley Online Library",
    "www.sciencedirect.com": "ScienceDirect",
    "linkinghub.elsevier.com": "Elsevier",
    "www.nature.com": "Nature",
    "www.sciengine.com": "Science China Press",
    "pubsonline.informs.org": "INFORMS",
}

FIGURE_KEYWORDS = ("system", "framework", "architecture", "overview", "method", "model", "pipeline", "design")


@dataclass
class CrossrefMatch:
    doi: str | None
    url: str | None
    publisher: str | None
    title: str


@dataclass
class AbstractResult:
    text: str
    source_url: str
    source_label: str


@dataclass
class FigureResult:
    relative_path: str
    caption: str
    source_url: str


class PublicationEnricher:
    def __init__(self, limit: int | None = None, verbose: bool = False) -> None:
        self.limit = limit
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Codex publication enrichment/1.0",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        self.crossref_cache: dict[str, CrossrefMatch | None] = {}
        self.arxiv_search_cache: dict[str, str | None] = {}
        self.openalex_cache: dict[str, AbstractResult | None] = {}
        self.publisher_cache: dict[str, AbstractResult | None] = {}
        self.last_arxiv_query = 0.0

    def log(self, message: str) -> None:
        if self.verbose:
            print(message)

    def request(self, url: str, **kwargs: Any) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(5):
            try:
                response = self.session.get(url, timeout=30, **kwargs)
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise requests.HTTPError(f"{response.status_code} for {url}")
                return response
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                time.sleep(1.0 + attempt * 1.5)
        if last_error is None:
            raise RuntimeError(f"request failed for {url}")
        raise last_error

    @staticmethod
    def normalize_title(title: str) -> str:
        text = re.sub(r"<[^>]+>", " ", title)
        text = html.unescape(text)
        text = text.replace("–", "-").replace("—", "-").lower()
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return " ".join(text.split())

    @staticmethod
    def clean_title(title: str) -> str:
        return re.sub(r"^\[[^\]]+\]\s*", "", title).strip()

    @staticmethod
    def split_front_matter(raw: str) -> tuple[str, str]:
        match = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", raw, re.S)
        if not match:
            raise ValueError("missing front matter")
        return match.group(1), match.group(2)

    @staticmethod
    def slug_from_permalink(permalink: str) -> str:
        return permalink.rstrip("/").rsplit("/", 1)[-1]

    @staticmethod
    def arxiv_id_from_url(url: str | None) -> str | None:
        if not url:
            return None
        match = re.search(r"arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5})(?:v\d+)?", url, re.I)
        if match:
            return match.group(1)
        match = re.search(r"arxiv\.org/pdf/([0-9]{4}\.[0-9]{4,5})(?:v\d+)?", url, re.I)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def doi_from_url(url: str | None) -> str | None:
        if not url:
            return None
        match = re.search(r"doi\.org/(10\.[^?#]+)", url, re.I)
        if match:
            return urllib.parse.unquote(match.group(1))
        return None

    def exact_crossref_match(self, title: str) -> CrossrefMatch | None:
        clean = self.clean_title(title)
        if clean in self.crossref_cache:
            return self.crossref_cache[clean]

        params = {"rows": 8, "query.bibliographic": clean}
        url = f"{CROSSREF_URL}?{urllib.parse.urlencode(params)}"
        match: CrossrefMatch | None = None

        try:
            response = self.request(url)
            response.raise_for_status()
            items = response.json().get("message", {}).get("items", [])
            normalized = self.normalize_title(clean)
            for item in items:
                item_titles = item.get("title") or []
                if not item_titles:
                    continue
                item_title = item_titles[0]
                if self.normalize_title(item_title) != normalized:
                    continue
                match = CrossrefMatch(
                    doi=item.get("DOI"),
                    url=item.get("URL"),
                    publisher=item.get("publisher"),
                    title=item_title,
                )
                break
        except Exception as exc:  # noqa: BLE001
            self.log(f"crossref lookup failed for {clean}: {exc}")

        self.crossref_cache[clean] = match
        return match

    def search_arxiv_exact(self, title: str) -> str | None:
        clean = self.clean_title(title)
        normalized_clean = self.normalize_title(clean)
        for override_title, override_id in ARXIV_TITLE_OVERRIDES.items():
            if self.normalize_title(override_title) == normalized_clean:
                return override_id
        if clean in self.arxiv_search_cache:
            return self.arxiv_search_cache[clean]

        elapsed = time.time() - self.last_arxiv_query
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

        params = {
            "search_query": f'ti:"{clean}"',
            "start": 0,
            "max_results": 3,
        }
        url = f"{ARXIV_SEARCH_URL}?{urllib.parse.urlencode(params)}"
        arxiv_id: str | None = None

        try:
            response = self.request(url)
            response.raise_for_status()
            entries = re.findall(
                r"<entry>.*?<id>http://arxiv\.org/abs/([^<]+)</id>.*?<title>(.*?)</title>",
                response.text,
                re.S,
            )
            normalized = self.normalize_title(clean)
            for candidate_id, candidate_title in entries:
                candidate_title = " ".join(candidate_title.split())
                if self.normalize_title(candidate_title) == normalized:
                    arxiv_id = candidate_id.split("v", 1)[0]
                    break
        except Exception as exc:  # noqa: BLE001
            self.log(f"arxiv search failed for {clean}: {exc}")
        finally:
            self.last_arxiv_query = time.time()

        self.arxiv_search_cache[clean] = arxiv_id
        return arxiv_id

    def arxiv_abstract(self, arxiv_id: str) -> AbstractResult | None:
        url = f"{ARXIV_ABS_PREFIX}{arxiv_id}"
        try:
            response = self.request(url)
            response.raise_for_status()
            match = re.search(
                r'<blockquote class="abstract mathjax">\s*<span class="descriptor">Abstract:</span>(.*?)</blockquote>',
                response.text,
                re.S,
            )
            if not match:
                return None
            text = self.clean_html_text(match.group(1))
            return AbstractResult(text=text, source_url=url, source_label="arXiv")
        except Exception as exc:  # noqa: BLE001
            self.log(f"arxiv abstract failed for {arxiv_id}: {exc}")
            return None

    def publisher_abstract(self, url: str, default_label: str | None = None) -> AbstractResult | None:
        if url in self.publisher_cache:
            return self.publisher_cache[url]

        result: AbstractResult | None = None
        try:
            response = self.request(url, allow_redirects=True)
            final_url = response.url
            html_text = response.text
            abstract = self.extract_publisher_abstract_text(html_text)
            if abstract:
                label = default_label or self.publisher_label(final_url)
                result = AbstractResult(text=abstract, source_url=final_url, source_label=label)
        except Exception as exc:  # noqa: BLE001
            self.log(f"publisher abstract failed for {url}: {exc}")

        self.publisher_cache[url] = result
        return result

    def openalex_abstract(self, title: str, doi: str | None) -> AbstractResult | None:
        cache_key = doi or self.clean_title(title)
        if cache_key in self.openalex_cache:
            return self.openalex_cache[cache_key]

        result: AbstractResult | None = None

        try:
            if doi:
                encoded = urllib.parse.quote(f"https://doi.org/{doi}", safe="")
                url = f"{OPENALEX_WORKS_URL}/{encoded}"
                response = self.request(url)
                if response.status_code == 200:
                    data = response.json()
                    abstract = self.openalex_text(data.get("abstract_inverted_index"))
                    if abstract:
                        result = AbstractResult(
                            text=abstract,
                            source_url=data.get("id", url),
                            source_label="OpenAlex",
                        )
            if result is None:
                params = {"search": self.clean_title(title), "per-page": 5}
                url = f"{OPENALEX_WORKS_URL}?{urllib.parse.urlencode(params)}"
                response = self.request(url)
                response.raise_for_status()
                normalized = self.normalize_title(title)
                for item in response.json().get("results", []):
                    item_title = item.get("title") or ""
                    if self.normalize_title(item_title) != normalized:
                        continue
                    abstract = self.openalex_text(item.get("abstract_inverted_index"))
                    if abstract:
                        result = AbstractResult(
                            text=abstract,
                            source_url=item.get("id", url),
                            source_label="OpenAlex",
                        )
                        break
        except Exception as exc:  # noqa: BLE001
            self.log(f"openalex lookup failed for {title}: {exc}")

        self.openalex_cache[cache_key] = result
        return result

    @staticmethod
    def openalex_text(inverted_index: dict[str, list[int]] | None) -> str | None:
        if not inverted_index:
            return None
        positioned_words: dict[int, str] = {}
        for word, positions in inverted_index.items():
            for position in positions:
                positioned_words[position] = word
        if not positioned_words:
            return None
        text = " ".join(positioned_words[index] for index in sorted(positioned_words))
        return PublicationEnricher.normalize_whitespace(text)

    def resolve_abstract(self, metadata: dict[str, Any], crossref: CrossrefMatch | None, arxiv_id: str | None) -> AbstractResult | None:
        title = metadata.get("title", "")
        paperurl = metadata.get("paperurl")
        if arxiv_id:
            abstract = self.arxiv_abstract(arxiv_id)
            if abstract:
                return abstract

        publisher_label = crossref.publisher if crossref and crossref.publisher else None
        candidate_urls = []
        if paperurl:
            candidate_urls.append(paperurl)
        if crossref and crossref.url and crossref.url not in candidate_urls:
            candidate_urls.append(crossref.url)

        for url in candidate_urls:
            abstract = self.publisher_abstract(url, default_label=publisher_label)
            if abstract:
                return abstract

        doi = self.doi_from_url(paperurl) or (crossref.doi if crossref else None)
        return self.openalex_abstract(title, doi)

    def resolve_arxiv_id(self, metadata: dict[str, Any]) -> str | None:
        paperurl = metadata.get("paperurl")
        title = metadata.get("title", "")
        arxiv_id = self.arxiv_id_from_url(paperurl)
        if arxiv_id:
            return arxiv_id
        return self.search_arxiv_exact(title)

    def extract_figure(self, arxiv_id: str, slug: str) -> FigureResult | None:
        pdf_path = self.download_arxiv_pdf(arxiv_id)
        if pdf_path is None:
            return None

        try:
            document = fitz.open(pdf_path)
        except Exception as exc:  # noqa: BLE001
            self.log(f"figure extraction failed to open {arxiv_id}: {exc}")
            return None

        best_score = -1
        best_payload: tuple[int, fitz.Rect, str] | None = None
        page_limit = min(5, document.page_count)

        for page_number in range(page_limit):
            page = document.load_page(page_number)
            blocks = sorted(page.get_text("blocks"), key=lambda item: (item[1], item[0]))
            for index, block in enumerate(blocks):
                caption = self.figure_caption(block[4])
                if not caption:
                    continue
                rect, score = self.figure_crop_for_caption(page, blocks, index, caption)
                if rect is None:
                    continue
                if score > best_score:
                    best_score = score
                    best_payload = (page_number, rect, caption)

        if best_payload is None or best_score < 55:
            return None

        page_number, rect, caption = best_payload
        page = document.load_page(page_number)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2.2, 2.2), clip=rect, alpha=False)
        image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGB")
        image = self.trim_white_border(image)

        output_dir = IMAGES_DIR / slug
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "featured.png"
        image.save(output_path)

        relative_path = f"/images/publications/{slug}/featured.png"
        return FigureResult(
            relative_path=relative_path,
            caption=caption,
            source_url=f"{ARXIV_ABS_PREFIX}{arxiv_id}",
        )

    def download_arxiv_pdf(self, arxiv_id: str) -> Path | None:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        pdf_path = TEMP_DIR / f"{arxiv_id}.pdf"
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            return pdf_path
        url = f"{ARXIV_PDF_PREFIX}{arxiv_id}.pdf"
        try:
            response = self.request(url)
            response.raise_for_status()
            pdf_path.write_bytes(response.content)
            return pdf_path
        except Exception as exc:  # noqa: BLE001
            self.log(f"pdf download failed for {arxiv_id}: {exc}")
            return None

    @staticmethod
    def figure_caption(block_text: str) -> str | None:
        text = PublicationEnricher.normalize_whitespace(block_text)
        if not re.search(r"^(fig(?:ure)?\.?\s*\d+)", text, re.I):
            return None
        return text

    def figure_crop_for_caption(
        self,
        page: fitz.Page,
        blocks: list[tuple[float, float, float, float, str, int, int]],
        caption_index: int,
        caption: str,
    ) -> tuple[fitz.Rect | None, int]:
        page_rect = page.rect
        caption_block = blocks[caption_index]
        caption_top = caption_block[1]
        caption_bottom = caption_block[3]
        page_height = page_rect.height
        page_width = page_rect.width

        if caption_top < page_height * 0.2:
            return None, 0

        body_candidates = []
        for block in blocks[:caption_index]:
            text = self.normalize_whitespace(block[4])
            width = block[2] - block[0]
            height = block[3] - block[1]
            if width <= page_width * 0.52:
                continue
            if len(text) < 40:
                continue
            if height > page_height * 0.22:
                continue
            if block[3] >= caption_top - 12:
                continue
            body_candidates.append(block)

        y0 = page_rect.y0 + page_height * 0.10
        if body_candidates:
            y0 = max(y0, body_candidates[-1][3] + 8)

        if caption_top - y0 < page_height * 0.20:
            y0 = max(page_rect.y0 + page_height * 0.08, caption_top - page_height * 0.42)

        rect = fitz.Rect(page_rect.x0 + page_width * 0.06, y0, page_rect.x1 - page_width * 0.06, caption_top - 6)
        if rect.height < page_height * 0.18 or rect.width < page_width * 0.60:
            return None, 0

        score = 0
        figure_number = re.search(r"fig(?:ure)?\.?\s*(\d+)", caption, re.I)
        if figure_number and figure_number.group(1) == "1":
            score += 45
        elif figure_number:
            score += 15

        lower_caption = caption.lower()
        if any(keyword in lower_caption for keyword in FIGURE_KEYWORDS):
            score += 25
        if len(caption) > 45:
            score += 10
        if page.number <= 2:
            score += 12
        if rect.height > page_height * 0.26:
            score += 12

        overlapping_body_blocks = 0
        for block in blocks:
            width = block[2] - block[0]
            height = block[3] - block[1]
            if width <= page_width * 0.52:
                continue
            if height > page_height * 0.22:
                continue
            block_rect = fitz.Rect(block[:4])
            if rect.intersects(block_rect):
                overlapping_body_blocks += 1
        if overlapping_body_blocks > 2:
            score -= 15

        if caption_bottom > page_height * 0.85:
            score += 6

        return rect, score

    @staticmethod
    def trim_white_border(image: Image.Image) -> Image.Image:
        background = Image.new(image.mode, image.size, (255, 255, 255))
        diff = ImageChops.difference(image, background)
        bbox = diff.getbbox()
        if not bbox:
            return image
        pad = 18
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(image.width, bbox[2] + pad)
        y1 = min(image.height, bbox[3] + pad)
        return image.crop((x0, y0, x1, y1))

    @staticmethod
    def clean_html_text(fragment: str) -> str:
        fragment = re.sub(r"<[^>]+>", " ", fragment)
        fragment = html.unescape(fragment)
        return PublicationEnricher.normalize_whitespace(fragment)

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        return " ".join(text.split())

    @staticmethod
    def extract_publisher_abstract_text(html_text: str) -> str | None:
        patterns = [
            r'<meta name="citation_abstract" content="([^"]+)"',
            r'<meta property="og:description" content="([^"]+)"',
            r'<meta name="description" content="([^"]+)"',
            r'"abstract"\s*:\s*"([^"]{120,})"',
            r'<section[^>]*class="Abstract"[^>]*>.*?<p>(.*?)</p>',
            r'<div[^>]*class="c-article-section__content"[^>]*>\s*<p>(.*?)</p>',
        ]
        for pattern in patterns:
            match = re.search(pattern, html_text, re.I | re.S)
            if not match:
                continue
            text = PublicationEnricher.clean_html_text(match.group(1))
            if PublicationEnricher.looks_like_abstract(text):
                return text
        return None

    @staticmethod
    def looks_like_abstract(text: str) -> bool:
        if not text or len(text) < 120:
            return False
        lowered = text.lower()
        rejected = (
            "cookie",
            "javascript",
            "sign in",
            "request rejected",
            "we use cookies",
            "skip to main content",
        )
        if any(token in lowered for token in rejected):
            return False
        return True

    @staticmethod
    def publisher_label(url: str) -> str:
        host = urllib.parse.urlparse(url).netloc.lower()
        for key, value in PUBLISHER_LABELS.items():
            if key in host:
                return value
        return host

    @staticmethod
    def parse_existing_front_matter(front_matter: str) -> dict[str, Any]:
        data = yaml.safe_load(front_matter) or {}
        if not isinstance(data, dict):
            raise ValueError("front matter is not a mapping")
        return data

    @staticmethod
    def strip_existing_enrichment(front_matter: str) -> list[str]:
        lines = front_matter.splitlines()
        output: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            match = re.match(r"^([A-Za-z0-9_]+):", line)
            if not match or match.group(1) not in ENRICHMENT_KEYS:
                output.append(line)
                index += 1
                continue

            is_block = bool(re.match(r"^[A-Za-z0-9_]+:\s*[>|]-?\s*$", line))
            index += 1
            if not is_block:
                continue
            while index < len(lines):
                next_line = lines[index]
                if re.match(r"^[A-Za-z0-9_]+:", next_line):
                    break
                index += 1
        return output

    def apply_enrichment(self, path: Path, metadata: dict[str, Any], enrichment: dict[str, str]) -> None:
        raw = path.read_text()
        front_matter, body = self.split_front_matter(raw)
        cleaned_lines = self.strip_existing_enrichment(front_matter)
        insertion_lines = self.serialize_enrichment(enrichment)

        anchor_index = -1
        for index, line in enumerate(cleaned_lines):
            if line.startswith("paperurl:"):
                anchor_index = index
                break
        if anchor_index == -1:
            for index, line in enumerate(cleaned_lines):
                if line.startswith("citation:"):
                    anchor_index = index
                    break
        if anchor_index == -1:
            anchor_index = len(cleaned_lines) - 1

        updated_lines = cleaned_lines[: anchor_index + 1] + insertion_lines + cleaned_lines[anchor_index + 1 :]
        updated_front_matter = "\n".join(updated_lines).rstrip()
        body_suffix = body if body else ""
        path.write_text(f"---\n{updated_front_matter}\n---\n{body_suffix}")

    @staticmethod
    def serialize_enrichment(values: dict[str, str]) -> list[str]:
        lines: list[str] = []
        key_order = [
            "arxiv_id",
            "abstract_source_label",
            "abstract_source_url",
            "abstract_text",
            "featured_figure",
            "featured_figure_caption",
            "featured_figure_source_url",
        ]

        for key in key_order:
            value = values.get(key)
            if not value:
                continue
            if key == "abstract_text":
                lines.append(f"{key}: |-")
                wrapped = textwrap.fill(value, width=92)
                lines.extend(f"  {line}" for line in wrapped.splitlines())
                continue
            if key == "featured_figure_caption" and len(value) > 120:
                lines.append(f"{key}: |-")
                wrapped = textwrap.fill(value, width=92)
                lines.extend(f"  {line}" for line in wrapped.splitlines())
                continue
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        return lines

    def enrich_publication(self, path: Path) -> dict[str, bool]:
        raw = path.read_text()
        front_matter, _ = self.split_front_matter(raw)
        metadata = self.parse_existing_front_matter(front_matter)

        arxiv_id = self.resolve_arxiv_id(metadata)
        crossref = self.exact_crossref_match(metadata.get("title", ""))
        abstract = self.resolve_abstract(metadata, crossref, arxiv_id)

        slug = self.slug_from_permalink(metadata["permalink"])
        figure = self.extract_figure(arxiv_id, slug) if arxiv_id else None

        enrichment: dict[str, str] = {}
        if arxiv_id:
            enrichment["arxiv_id"] = arxiv_id
        if abstract:
            enrichment["abstract_source_label"] = abstract.source_label
            enrichment["abstract_source_url"] = abstract.source_url
            enrichment["abstract_text"] = abstract.text
        if figure:
            enrichment["featured_figure"] = figure.relative_path
            enrichment["featured_figure_caption"] = figure.caption
            enrichment["featured_figure_source_url"] = figure.source_url

        self.apply_enrichment(path, metadata, enrichment)
        return {"has_abstract": bool(abstract), "has_figure": bool(figure), "has_arxiv": bool(arxiv_id)}

    def run(self) -> int:
        publications = sorted(PUBLICATIONS_DIR.glob("*.md"))
        if self.limit is not None:
            publications = publications[: self.limit]

        counts = {"processed": 0, "abstract": 0, "figure": 0, "arxiv": 0}
        missing_abstract: list[str] = []
        missing_figure: list[str] = []

        for index, path in enumerate(publications, start=1):
            result = self.enrich_publication(path)
            counts["processed"] += 1
            counts["abstract"] += int(result["has_abstract"])
            counts["figure"] += int(result["has_figure"])
            counts["arxiv"] += int(result["has_arxiv"])

            if not result["has_abstract"]:
                missing_abstract.append(path.name)
            if result["has_arxiv"] and not result["has_figure"]:
                missing_figure.append(path.name)

            print(
                f"[{index:02d}/{len(publications)}] "
                f"{path.name}: abstract={'yes' if result['has_abstract'] else 'no'}, "
                f"arxiv={'yes' if result['has_arxiv'] else 'no'}, "
                f"figure={'yes' if result['has_figure'] else 'no'}"
            )

        print("\nSUMMARY")
        print(json.dumps(counts, indent=2))
        if missing_abstract:
            print("\nMISSING_ABSTRACT")
            for item in missing_abstract:
                print(item)
        if missing_figure:
            print("\nMISSING_FIGURE_FOR_ARXIV")
            for item in missing_figure:
                print(item)
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich publication pages with abstracts and arXiv figures.")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N publications.")
    parser.add_argument("--verbose", action="store_true", help="Print lookup failures and retries.")
    args = parser.parse_args()

    enricher = PublicationEnricher(limit=args.limit, verbose=args.verbose)
    return enricher.run()


if __name__ == "__main__":
    raise SystemExit(main())
