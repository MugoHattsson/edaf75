with import <nixpkgs> {};

let
  python = python311;
in
pkgs.mkShell {
  name = "pip-env";
  buildInputs = with pkgs; [
    python311Packages.virtualenv
    poetry
  ];
  src = null;
  shellHook = ''
    # Allow the use of wheels.
    SOURCE_DATE_EPOCH=$(date +%s)

    VENV=venv
    if test ! -d $VENV; then
      virtualenv $VENV
    fi
    source ./$VENV/bin/activate

    # export PYTHONPATH=`pwd`/$VENV/${python.sitePackages}/:$PYTHONPATH
    export LD_LIBRARY_PATH=${lib.makeLibraryPath [stdenv.cc.cc]}
  '';
}
