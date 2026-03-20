{
  python-pin,
  version,
  py-deps,
  anki-lib,
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
  # Add anki to PYTHONPATH at runtime.
  makeWrapperArgs = [
    "--prefix PYTHONPATH : ${anki-lib}/lib/python3.13/site-packages"
  ];
  doCheck = false;
}
