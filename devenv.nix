{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/packages/
  packages = [
    pkgs.git
    pkgs.llama-cpp
  ];

  dotenv.enable = true;


  # https://devenv.sh/languages/
  languages.javascript.enable=true;
  languages.javascript.npm.enable=true;
  languages.javascript.npm.package=pkgs.nodejs_20;
  languages.javascript.pnpm.enable=true;

  languages.python.enable=true;
  languages.python.package=pkgs.python311;
  languages.python.uv.enable=true;
  languages.python.uv.sync.enable=true;
  languages.python.venv.enable=true;
  languages.python.venv.requirements=''
    minio==7.2.11
    openai==1.55.0
    llama-index-core==0.10.68
    llama-index-readers-file==0.1.33
    fastapi==0.111.0
    pydantic==2.8.2
    pydantic-settings==2.3.4
    boto3==1.34.26
    llama-index-embeddings-bedrock==0.2.1
    llama-index-llms-bedrock==0.1.13
    llama-index-llms-openai==0.1.31
    llama-index-llms-mistralai==0.1.20
    llama-index-embeddings-openai==0.1.11
    llama-index-vector-stores-qdrant==0.2.17
    fastapi-utils>=0.8.0
  '';

  languages.java.enable=true;
  languages.java.gradle.enable=true;
  languages.java.jdk.package=pkgs.jdk21_headless;

  processes = {
    s3.exec = "minio server --address :9090 --console-address :9001 /opt/ps_ai/drive";
    llama-cpp.exec = "llama-server -m /opt/ps_ai/models/llama-2-7b.Q6_K.gguf -m $PATH_GGUF_MODEL --port 8088 --embeddings";
  };
  # See full reference at https://devenv.sh/reference/options/
}
