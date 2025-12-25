# Desktop App Icons

Place application icons here:

- `icon.png` - 512x512 PNG for Linux
- `icon.icns` - macOS icon bundle
- `icon.ico` - Windows icon file

## Creating Icons

You can use online tools to convert a base PNG to platform-specific formats:

- https://cloudconvert.com/png-to-icns (for macOS)
- https://cloudconvert.com/png-to-ico (for Windows)
- https://iconverticons.com/online/

Or use command-line tools:

### macOS (.icns)
```bash
# Install imagemagick
brew install imagemagick

# Create iconset
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# Convert to icns
iconutil -c icns icon.iconset
```

### Windows (.ico)
```bash
# Using ImageMagick
convert icon.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

### Temporary Placeholder
Until you have custom icons, electron-builder will use default icons.
