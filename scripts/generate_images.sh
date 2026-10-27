#!/bin/sh
# Generate website variants without changing the licensed source photographs.
# Requires ImageMagick 7 and Fontconfig. Run from the repository root.
set -eu

for size in 16 32; do
  magick assets/images/app-icon.png -resize "${size}x${size}" -strip "assets/images/favicon-${size}.png"
done
magick assets/images/app-icon.png -resize 180x180 -strip assets/images/apple-touch-icon.png
magick assets/images/app-icon.png -resize 160x160 -strip assets/images/app-icon-160.png
magick assets/images/brand-illustration.png -resize 104x104 -strip assets/images/brand-104.png

for size in 400 714; do
  magick assets/images/rubber-plant.jpg -resize "${size}x>" -strip -quality 80 "assets/images/rubber-plant-${size}.webp"
done
for plant in monstera pilea; do
  for size in 320 640; do
    magick "assets/images/${plant}.jpg" -resize "${size}x>" -strip -quality 80 "assets/images/${plant}-${size}.webp"
  done
done

for screen in plants care catalog; do
  for size in 400 642; do
    magick "assets/images/app-${screen}.jpg" -resize "${size}x>" -strip -quality 85 "assets/images/app-${screen}-${size}.webp"
  done
done

# A static landscape preview using the existing brand artwork and system fonts.
serif_font=$(fc-match -f '%{file}' serif)
sans_font=$(fc-match -f '%{file}' sans)
test -f "$serif_font"
test -f "$sans_font"
magick -size 1200x630 xc:'#f7f7ef' \
  \( assets/images/app-icon.png -resize 360x360 \) -gravity northwest -geometry +68+135 -composite \
  -font "$serif_font" -fill '#203e30' -pointsize 62 -annotate +485+235 'Leafy & Me' \
  -pointsize 40 -annotate +485+315 'Plant care at your pace.' \
  -font "$sans_font" -fill '#315b3e' -pointsize 25 -annotate +485+385 'Free for iPhone and iPad' \
  -pointsize 22 -annotate +485+440 'leafyandme.com' \
  -strip -depth 8 -colors 256 -define png:compression-level=9 assets/images/social-preview.png
