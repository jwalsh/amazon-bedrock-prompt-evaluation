#!/bin/bash

# Validate prompts using xmllint
xmllint --noout --dtdvalid prompts.dtd prompts.xml

# Check the exit status
if [ $? -eq 0 ]; then
    echo "All prompts are valid according to the DTD."
else
    echo "Validation failed. Please check the error messages above."
fi
