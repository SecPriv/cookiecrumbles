FROM nixos/nix
ADD ./shell.nix /
RUN nix-env -if /shell.nix -A buildInputs
CMD ["nix-shell", "/shell.nix"]
