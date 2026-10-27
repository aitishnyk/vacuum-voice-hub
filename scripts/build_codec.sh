#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "${1:?Usage: sh scripts/build_codec.sh SOURCE_DIRECTORY}" && pwd)
PREFIX="$ROOT/runtime"
mkdir -p "$PREFIX"
cd "$ROOT"
tar xf libogg-1.3.5.tar.xz
tar xf libvorbis-1.3.7.tar.xz
tar xf lame-3.100.tar.gz
tar xf ffmpeg-7.1.tar.xz
cd "$ROOT/libogg-1.3.5"
./configure --prefix="$PREFIX" --disable-shared --enable-static
make -j6
make install
cd "$ROOT/libvorbis-1.3.7"
PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig" ./configure --prefix="$PREFIX" --disable-shared --enable-static --with-ogg="$PREFIX"
make -j6
make install
cd "$ROOT/lame-3.100"
./configure --prefix="$PREFIX" --disable-shared --enable-static --disable-frontend --disable-decoder
make -j6
make install
cd "$ROOT/ffmpeg-7.1"
PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig" ./configure --prefix=../runtime --pkg-config-flags=--static --disable-everything --disable-autodetect --disable-x86asm --disable-doc --disable-debug --disable-network --enable-ffmpeg --enable-avcodec --enable-avformat --enable-avfilter --enable-swresample --enable-protocol=file,pipe --enable-demuxer=wav,ogg,mp3,flac,mov,aac --enable-decoder=pcm_s16le,pcm_s24le,pcm_f32le,vorbis,mp3,mp3float,flac,aac,opus,alac --enable-encoder=pcm_s16le,libvorbis,libmp3lame --enable-muxer=wav,ogg,mp3 --enable-parser=mpegaudio,vorbis,flac,aac,opus --enable-filter=aresample,aformat,volume,atrim,anull --enable-libvorbis --enable-libmp3lame --extra-cflags=-I../runtime/include --extra-ldflags=-L../runtime/lib
make -j6
make install
"$PREFIX/bin/ffmpeg" -L
