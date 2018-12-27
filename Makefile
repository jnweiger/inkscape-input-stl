#


.PHONY: test

test:
	python inkscape-input-stl.py -l 1 --rx 180 test/xwing_templates_RANGE_3_.stl
	@echo "Expected output:                   48 polygons in 9 layers converted to paths."
