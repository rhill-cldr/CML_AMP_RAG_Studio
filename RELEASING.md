# Release process for the RAG Studio AMP

* Get `main` into the state to be released
* Publish a release from the `main` branch with the desired version to release
* Verify the release in a CML workspace, deploying from `main`
* Merge main into the `release/1` branch via a pull request, keeping the version file contents from main
  * Let the PR build run, to verify no merge conflicts took place
* If desired: publish a new release with the same version from the `release/1` branch to make sure the code matches the release bundles.

