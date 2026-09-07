{
  description = "ML-среда внутри FHS-окружения с автонастройкой VS Code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";

      pkgs = import nixpkgs {
        inherit system;
        config = { allowUnfree = true; };
      };

      # 1. Настройка VS Code
      my-vscode = pkgs.vscode-with-extensions.override {
        vscodeExtensions = with pkgs.vscode-extensions; [
          ms-azuretools.vscode-containers
          jnoortheen.nix-ide
          ms-python.python
          ms-python.black-formatter
          ms-python.vscode-pylance
          anthropic.claude-code
        ];
      };

      # 2. Создание изолированного FHS-окружения
      fhsEnv = pkgs.buildFHSEnv {
        name = "ml-fhs-env";
        targetPkgs = pkgs: [
          my-vscode
          pkgs.pyright
          pkgs.python313
          pkgs.uv
          
          # Системные библиотеки, нужные для ML-пакетов (PyTorch, Cuda-драйверы и т.д.)
          pkgs.stdenv.cc.cc.lib
          pkgs.zlib
          pkgs.glib
          pkgs.glibc
          pkgs.sqlite
        ];
        # Скрипт, который выполнится при входе в FHS
        runScript = "bash";
      };
    in
    {
      # 3. Обертка в devShell для работы команды `nix develop`
      devShells.${system}.default = pkgs.mkShell {
        packages = [ fhsEnv ];

        shellHook = ''
          # Автоматически настраиваем VS Code для этого проекта
          mkdir -p .vscode
          cat <<EOF > .vscode/settings.json
          {
            "python.defaultInterpreterPath": "''${workspaceFolder}/.venv/bin/python",
            "python.languageServer": "Pylance",
            "nix.enableLanguageServer": true,
            "nix.serverPath": "nixd"
          }
          EOF

          echo "✅ Конфиги VS Code обновлены. Входим в FHS-окружение..."
          
          # Автоматически запускаем наше FHS-окружение при входе в nix develop
          exec ${fhsEnv}/bin/ml-fhs-env
        '';
      };
    };
}