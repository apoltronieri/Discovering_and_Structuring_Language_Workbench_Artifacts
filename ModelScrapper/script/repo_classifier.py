import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN não encontrado")

HEADERS = {"Authorization": f"token {TOKEN}"}

PATTERNS = {
    "dsl": [
        "behavior.mps",
        "typesystem.mps",
        "editor.mps",
        ".xtext",
        ".mwe2",
        ".langium",
        "src/main/xtext",
        "src/grammar"
    ],
    "metamodel": [
        ".ecore",
        ".genmodel"
    ],
    "parser": [
        ".g4",
        ".g",
        "lexer rule",
        "parser rule"
    ],
    "framework": [
        "/core",
        "/api",
        "/runtime",
        "/lib",
        "/plugins"
    ],
    "tutorial": [
        "/examples/",
        "/samples/",
        "/demo",
        "/tutorial",
        "/quickstart"
    ]
}

def infer_abstraction_level(artifacts):
    has_pim = any(a in artifacts for a in (
        ".mps",
        "structure.mps",
        "editor.mps",
        "behavior.mps",
        ".xtext",
        ".langium",
        ".ecore",
        ".genmodel"
    ))

    has_psm = any(a in artifacts for a in (
        ".g4",
        ".g",
        "/runtime",
        "/plugins",
        "/lib",
        "/core",
        "/api"
    ))

    if has_pim and has_psm:
        return "PSM"
    if has_psm:
        return "PSM"
    if has_pim:
        return "PIM"
    return "CIM"


def classify_repo_from_api(owner: str, name: str):
    url = f"https://api.github.com/repos/{owner}/{name}/git/trees/HEAD?recursive=1"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return "unknown", []

    tree = r.json().get("tree", [])
    paths = [item.get("path", "").lower() for item in tree]
    joined = " ".join(paths)

    artifacts = []

    for group in PATTERNS.values():
        for p in group:
            if p in joined:
                artifacts.append(p)

    classification = "unknown"
    struct = "structure.mps" in joined

    if any(p in joined for p in PATTERNS["dsl"]):
        classification = "dsl"
    elif any(p in joined for p in PATTERNS["metamodel"]):
        classification = "metamodel"
    elif struct:
        classification = "metamodel"
    elif any(p in joined for p in PATTERNS["parser"]):
        classification = "parser"
    elif any(p in joined for p in PATTERNS["framework"]):
        classification = "framework"
    elif any(p in joined for p in PATTERNS["tutorial"]):
        classification = "tutorial"

    return classification, artifacts


def run_classifier(input_json: str, output_json: str, use_api: bool = False):
    with open(input_json, "r") as f:
        repos = json.load(f)

    out = []

    for r in repos:
        owner = r["owner"]
        name = r["name"]

        if use_api:
            classification, artifacts = classify_repo_from_api(owner, name)
        else:
            classification = "unknown"
            artifacts = []

        abstraction = infer_abstraction_level(artifacts)

        out.append({
            "owner": owner,
            "name": name,
            "url": r.get("url"),
            "framework_detected": r.get("framework"),
            "classification": classification,
            "artifacts_detected": artifacts,
            "abstraction_level": abstraction
        })

    with open(output_json, "w") as f:
        json.dump(out, f, indent=4)

    print(f"Classificação salva em {output_json}")


if __name__ == "__main__":
    run_classifier(
        input_json="saida.json",
        output_json="classified_output.json",
        use_api=True
    )