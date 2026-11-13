{
  description = "RuneLite plugin development environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          jdk = pkgs.jdk11;
          gradle = pkgs.gradle_8-unwrapped.override { java = jdk; };
          nativeLibraries = with pkgs; [
            libGL
            libx11
            libxcursor
            libxext
            libxi
            libxrandr
            libxrender
            libxtst
            libxxf86vm
            alsa-lib
            stdenv.cc.cc.lib
          ];
          authLibraries = with pkgs; [
            glibc
            openssl
            webkitgtk_4_1
            gtk3
            libsoup_3
            glib
            curl
            stdenv.cc.cc.lib
          ];
        in {
          default = pkgs.mkShell {
            packages = [ jdk gradle pkgs.gnumake pkgs.python3 pkgs.git pkgs.patchelf ];
            JAVA_HOME = "${jdk}";
            RUNELITE_JAGEXAUTH_INTERPRETER = pkgs.stdenv.cc.bintools.dynamicLinker;
            RUNELITE_JAGEXAUTH_LIBRARY_PATH = pkgs.lib.makeLibraryPath authLibraries;
            shellHook = ''
              export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath nativeLibraries}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
              export GIO_EXTRA_MODULES="${pkgs.glib-networking}/lib/gio/modules''${GIO_EXTRA_MODULES:+:$GIO_EXTRA_MODULES}"
              export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}:${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:''${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
            '';
          };
        });
    };
}
