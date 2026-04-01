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
        py-deps = with python-pin.pkgs; [
          yoyo-migrations
        ];
        python-with-deps = python-pin.withPackages (_: py-deps);
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
          '';
          buildInputs = [
            (pkgs.buildEnv {
              name = "lixue-devshell";
              paths = [
                pkgs.just
                pkgs.ruff
                python-with-deps
              ];
            })
          ];
        };
      }
    );
}
