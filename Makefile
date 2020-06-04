.PHONY: docs

docs:
	@cd docs && make html

release:
	@VERSION=$$(python -c "import rltk;print(rltk.__version__)") && git tag $$VERSION
