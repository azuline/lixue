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
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (_: super: {
              sqlc-gen-python = super.writeShellScriptBin "sqlc-gen-python" ''
                cd "$LIXUE_ROOT"
                exec ${python-with-deps}/bin/python -m tools.codegen_db_plugin "$@"
              '';
            })
          ];
        };
        python-pin = pkgs.python313;
        py-deps = with python-pin.pkgs; [
          # Runtime deps.
          click
          yoyo-migrations
          # Codegen deps.
          betterproto
          jinja2
          # Dev tools.
          setuptools
          pytest
          pytest-timeout
          pytest-cov
          pytest-xdist
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
            export PYTHONPATH="$LIXUE_ROOT:''${PYTHONPATH:-}"
          '';
          buildInputs = [
            (pkgs.buildEnv {
              name = "lixue-devshell";
              paths = [
                pkgs.just
                pkgs.ruff
                pkgs.sqlc
                pkgs.sqlc-gen-python
                python-with-deps
              ];
            })
          ];
        };
      }
    );
}
