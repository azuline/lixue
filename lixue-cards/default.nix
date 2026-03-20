{
  python-pin,
  version,
  py-deps,
}:

python-pin.pkgs.buildPythonApplication {
  pname = "lixue-cards";
  version = version;
  src = ./.;
  pyproject = true;
  build-system = [ py-deps.setuptools ];
  propagatedBuildInputs = [
    py-deps.click
  ];
  doCheck = false;
}
