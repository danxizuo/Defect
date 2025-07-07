import argparse
import hashlib
import json
import os


def compute_md5(path: str) -> str:
    """Return the MD5 hash of a file."""
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def collect_mapping(ref_dir: str, def_dir: str) -> dict:
    mapping = {}
    for name in os.listdir(ref_dir):
        ref_path = os.path.join(ref_dir, name)
        if not os.path.isfile(ref_path):
            continue
        base, _ = os.path.splitext(name)
        # try jpg and png in defect directory
        candidates = [
            os.path.join(def_dir, base + ext) for ext in ('.jpg', '.png')
        ]
        defect_path = next((c for c in candidates if os.path.exists(c)), None)
        if defect_path:
            mapping[compute_md5(ref_path)] = defect_path
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build MD5 mapping of reference images to defect images"
    )
    parser.add_argument(
        'output', help='Path to output JSON mapping file'
    )
    parser.add_argument(
        '--pairs', nargs=2, action='append', metavar=('REF_DIR', 'DEF_DIR'),
        required=True, help='Reference and defect directory pair'
    )
    args = parser.parse_args()

    result = {}
    for ref_dir, def_dir in args.pairs:
        result.update(collect_mapping(ref_dir, def_dir))

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)


if __name__ == '__main__':
    main()
