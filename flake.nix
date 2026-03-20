{
  description = "lixue";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        python-pin = pkgs.python313;
        version = nixpkgs.lib.strings.removeSuffix "\n" (
          builtins.readFile ./lixue-cards/lixue_cards/.version
        );
        anki-lib = pkgs.anki.lib;
        py-deps = with python-pin.pkgs; {
          inherit
            # Runtime deps.
            click
            setuptools
            # Dev tools.
            pytest
            pytest-timeout
            pytest-cov
            pytest-xdist
            syrupy
            ;
        };
        python-with-deps = python-pin.withPackages (_: pkgs.lib.attrsets.mapAttrsToList (a: b: b) py-deps);
      in
      {
        devShells.default = pkgs.mkShell {
          shellHook = ''
            find-up () {
              path=$(pwd)
              while [[ "$path" != "" && ! -e "$path/$1" ]]; do
                path=''${path%/*}
              done
              echo "$path"
            }
            export LIXUE_ROOT="$(find-up flake.nix)"
            export PYTHONPATH="$LIXUE_ROOT/lixue-cards:''${PYTHONPATH:-}"
            export PYTHONPATH="${anki-lib}/lib/python3.13/site-packages:$PYTHONPATH"
          '';
          buildInputs = [
            (pkgs.buildEnv {
              name = "lixue-devshell";
              paths = [
                pkgs.ruff
                pkgs.ty
                python-with-deps
              ];
            })
          ];
        };
        packages = rec {
          lixue-cards = pkgs.callPackage ./lixue-cards {
            inherit
              version
              python-pin
              py-deps
              anki-lib
              ;
          };
          all = pkgs.buildEnv {
            name = "lixue-all";
            paths = [
              lixue-cards
            ];
          };
        };
      }
    );
}
