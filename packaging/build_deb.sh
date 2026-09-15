# Monta um pacote .deb a partir do binário já gerado pelo PyInstaller

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSAO="${VERSAO:-1.0.0}"
ARQUITETURA="${ARQUITETURA:-amd64}"
NOME_PKG="sticker-notes"
SAIDA="$RAIZ/dist/${NOME_PKG}_${VERSAO}_${ARQUITETURA}"

if [ ! -f "$RAIZ/dist/sticker-notes" ]; then
    echo "Binário não encontrado em dist/sticker-notes." >&2
    echo "Rode antes: pyinstaller --noconfirm --clean packaging/sticker-notes.spec" >&2
    exit 1
fi

rm -rf "$SAIDA"
mkdir -p "$SAIDA/DEBIAN"
mkdir -p "$SAIDA/usr/bin"
mkdir -p "$SAIDA/usr/share/applications"
mkdir -p "$SAIDA/usr/share/icons/hicolor/256x256/apps"

cp "$RAIZ/dist/sticker-notes" "$SAIDA/usr/bin/sticker-notes"
chmod 755 "$SAIDA/usr/bin/sticker-notes"
cp "$RAIZ/packaging/linux/sticker-notes.desktop" "$SAIDA/usr/share/applications/sticker-notes.desktop"
cp "$RAIZ/packaging/icons/sticker-notes.png" "$SAIDA/usr/share/icons/hicolor/256x256/apps/sticker-notes.png"

cat > "$SAIDA/DEBIAN/control" <<EOF
Package: ${NOME_PKG}
Version: ${VERSAO}
Section: utils
Priority: optional
Architecture: ${ARQUITETURA}
Maintainer: Ana Beatriz <abeatriz.frez@gmail.com>
Description: Notas adesivas para a área de trabalho.
 Aplicativo de notas adesivas com várias cores, formatação de texto,
 listas de tarefas e opção de manter sempre visível.
EOF

dpkg-deb --build --root-owner-group "$SAIDA"
echo "Gerado: ${SAIDA}.deb"
