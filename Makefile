.PHONY: docs

docs:
	@cd docs && make html

run-docs:
	@cd docs/_build/html && python -m http.server 8080 --bind localhost

release:
	@VERSION=$$(python -c "import rltk;print(rltk.__version__)") && git tag $$VERSION
