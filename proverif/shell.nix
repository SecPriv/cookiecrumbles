let 
  pin = fetchTarball { url = "https://github.com/nixos/nixpkgs/archive/a2e281f5770247855b85d70c43454ba5bff34613.tar.gz"; };
  pkgs = import (pin) {};
in
pkgs.mkShell rec {
    name = "proverif";
    buildInputs = with pkgs; [ coreutils gnused gcc gnumake proverif bat ];
}
