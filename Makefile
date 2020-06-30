pdfs := mro.pdf super.pdf

all: fmt

fmt:
	isort --recursive .
	autoflake --recursive --in-place --remove-all-unused-imports --remove-unused-variables .
	black .

lint:
	flake8
	isort --recursive . --check-only
	black . --check

pdfs: $(pdfs)

%.pdf: %.dot
	dot $< -T pdf -o $@

%.dot: graph.py
	./graph.py $* > $@


clean:
	rm -f $(pdfs)
