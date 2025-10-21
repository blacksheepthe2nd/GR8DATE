#!/usr/bin/env bash
set -euo pipefail

ARCHIVE="tar"        # tar | zip
WITH_GIT="no"
LABEL=""
PROJECT_ROOT="$(pwd)"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"

while (( "$#" )); do
  case "$1" in
    --archive) ARCHIVE="${2:-tar}"; shift 2;;
    --with-git) WITH_GIT="yes"; shift;;
    --name) LABEL="${2:-}"; shift 2;;
    -h|--help) echo "Usage: $0 [--archive tar|zip] [--with-git] [--name LABEL]"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

mkdir -p "$BACKUP_DIR"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/gr8date_backup.XXXXXX")"
cleanup() { rm -rf "$STAGE"; }
trap cleanup EXIT

DB_PATH=""
if [[ -n "${DB_URL:-}" ]]; then
  DB_PATH="$DB_URL"
else
  if [[ -f "manage.py" ]]; then
    set +e
    DB_PATH="$(python manage.py shell -c 'from django.conf import settings; n=settings.DATABASES["default"]["NAME"]; print(n)')"
    RES=$?
    set -e
    [[ $RES -ne 0 || -z "$DB_PATH" ]] && DB_PATH=""
  fi
fi

if [[ -n "$DB_PATH" && ! -f "$DB_PATH" && "$DB_PATH" != /* ]]; then
  if [[ -f "$DB_PATH" ]]; then
    DB_PATH="$(cd "$(dirname "$DB_PATH")" && pwd)/$(basename "$DB_PATH")"
  fi
fi

echo "• Staging project…"
mkdir -p "$STAGE/project"
rsync -a --exclude '__pycache__' --exclude '*.pyc' core/   "$STAGE/project/core/"   2>/dev/null || true
rsync -a --exclude '__pycache__' --exclude '*.pyc' pages/  "$STAGE/project/pages/"  2>/dev/null || true
rsync -a templates/ "$STAGE/project/templates/"            2>/dev/null || true
rsync -a blog/      "$STAGE/project/blog/"                 2>/dev/null || true

for f in manage.py requirements.txt requirements*.in Pipfile* pyproject.toml poetry.lock README* LICENSE*; do
  [[ -e "$f" ]] && rsync -a "$f" "$STAGE/project/" || true
done

rsync -a --exclude 'staticfiles' static/ "$STAGE/project/static/" 2>/dev/null || true
rsync -a media/ "$STAGE/project/media/" 2>/dev/null || true

if command -v pip >/dev/null 2>&1; then
  pip freeze > "$STAGE/project/requirements.freeze.txt" || true
fi

mkdir -p "$STAGE/db"
if [[ -n "$DB_PATH" && -f "$DB_PATH" ]]; then
  echo "• Detected SQLite at: $DB_PATH"
  cp -p "$DB_PATH" "$STAGE/db/db.sqlite3"
  if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$DB_PATH" ".dump" > "$STAGE/db/db.sqlite3.dump.sql" || true
  fi
else
  echo "• No file-based SQLite detected (DB_PATH='${DB_PATH:-}')."
fi

if [[ "$WITH_GIT" == "yes" && -d ".git" && $(command -v git) ]]; then
  echo "• Creating git bundle…"
  mkdir -p "$STAGE/git"
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 && \
    git bundle create "$STAGE/git/repo.bundle" --all || true
  git status --porcelain=v1 > "$STAGE/git/status.txt" || true
  git rev-parse HEAD > "$STAGE/git/HEAD.txt" || true
fi

SAFE_LABEL=""
[[ -n "$LABEL" ]] && SAFE_LABEL="_${LABEL//[^a-zA-Z0-9._-]/-}"
BASENAME="gr8date_backup_${STAMP}${SAFE_LABEL}"

OUT_TAR="${BACKUP_DIR}/${BASENAME}.tar.gz"
OUT_ZIP="${BACKUP_DIR}/${BASENAME}.zip"

echo "• Archiving…"
if [[ "$ARCHIVE" == "zip" ]]; then
  (cd "$STAGE" && zip -qry "$OUT_ZIP" .)
  OUT="$OUT_ZIP"
else
  (cd "$STAGE" && tar -czf "$OUT_TAR" .)
  OUT="$OUT_TAR"
fi

SUMCMD=""
if command -v shasum >/dev/null 2>&1; then
  SUMCMD="shasum -a 256"
elif command -v sha256sum >/devnull 2>&1; then
  SUMCMD="sha256sum"
fi
if [[ -n "$SUMCMD" ]]; then
  $SUMCMD "$OUT" > "${OUT}.sha256"
  echo "• Checksum: ${OUT}.sha256"
fi

echo "✅ Backup written to: $OUT"
