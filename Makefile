.PHONY: help zeitlabs requirements test-python quality test

.DEFAULT_GOAL := help

# The tests run against openedx-zeitlabs-payments main: its package and its edx-platform mocks, which are not
# published, come from the same checkout.
ZEITLABS_REPO := https://github.com/zeit-labs/openedx-zeitlabs-payments.git
ZEITLABS_BRANCH := main
ZEITLABS_DIR := .zeitlabs
ZEITLABS_MOCKS := $(ZEITLABS_DIR)/test_utils/edx_platform_mocks

# The code is imported with the edx-platform mocks on the path, as in the LMS with the real platform.
PYTHON_ENV := PYTHONPATH=.:$(ZEITLABS_MOCKS) DJANGO_SETTINGS_MODULE=test_settings
QUALITY_PATHS := eox_paygate tests test_settings.py setup.py

help: ## display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-14s %s\n", $$1, $$2}'

zeitlabs: ## check out openedx-zeitlabs-payments main into .zeitlabs
	@if [ -d $(ZEITLABS_DIR)/.git ]; then \
		git -C $(ZEITLABS_DIR) fetch --depth 1 origin $(ZEITLABS_BRANCH) && git -C $(ZEITLABS_DIR) reset --hard FETCH_HEAD; \
	else \
		git clone --depth 1 --branch $(ZEITLABS_BRANCH) $(ZEITLABS_REPO) $(ZEITLABS_DIR); \
	fi

requirements: zeitlabs ## install the test and quality requirements in the current virtualenv
	pip install -r requirements/test.in -r requirements/quality.in
	pip install $(ZEITLABS_DIR)
	pip install -e .

test-python: ## run the Python tests in the current virtualenv
	$(PYTHON_ENV) pytest

quality: ## check the code style in the current virtualenv
	$(PYTHON_ENV) pylint $(QUALITY_PATHS)
	pycodestyle $(QUALITY_PATHS)
	pydocstyle $(QUALITY_PATHS)
	isort --check-only --diff $(QUALITY_PATHS)

test: quality test-python ## run the quality checks and the Python tests in the current virtualenv
