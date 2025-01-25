create_lambda_layer:
	@echo "Creating the layer ..."
	./aws/1-install.sh
	./aws/2-package.sh
	rm -rf create_layer/
	rm -rf python/

publish_lambda_layer:
	@echo "Publishing the layer ..."
	LAYER_ARN=$$(aws lambda publish-layer-version \
		--layer-name "google-genai-langchain-qdrant" \
		--description "Layer having Google GenAI, Langchain and Qdrant installed, optimized for Lambda functions" \
		--zip-file "fileb://my_layer.zip" \
		--compatible-runtimes python3.11 \
		--query "LayerVersionArn" --output text); \
	echo "Layer ARN: $$LAYER_ARN"
	rm -f my_layer.zip

update_lambda_function:
	@echo "Packaging the Lambda functions..."
	zip -r my_function.zip src/ processResume.py searchResume.py .cache/

	@echo "Updating the Lambda functions..."
	LAYER_ARN=$$(aws lambda list-layer-versions \
		--layer-name "google-genai-langchain-qdrant" \
		--query "LayerVersions[0].LayerVersionArn" \
		--output text); \
	
	echo "Using Layer ARN: $$LAYER_ARN"; \
	aws lambda update-function-code \
		--function-name searchResume \
		--zip-file fileb://my_function.zip; \
	
	aws lambda update-function-configuration \
		--function-name searchResume \
		--runtime python3.11 \
		--role arn:aws:iam::977099032416:role/Lambda-S3-ReadOnly
		--handler searchResume.handler \
		--layers $$LAYER_ARN \
		--environment Variables="{QDRANT_URL=$$QDRANT_URL,QDRANT_API_KEY=$$QDRANT_API_KEY,COLLECTION_NAME=$$COLLECTION_NAME,GOOGLE_API_KEY=$$GOOGLE_API_KEY,FASTEMBED_CACHE=$$FASTEMBED_CACHE}"; \
	
	aws lambda update-function-code \
		--function-name processResume \
		--zip-file fileb://my_function.zip; \
	
	aws lambda update-function-configuration \
		--function-name processResume \
		--runtime python3.11 \
		--role arn:aws:iam::977099032416:role/Lambda-FullyAccess-S3 \
		--handler processResume.handler \
		--layers $$LAYER_ARN \
		--environment Variables="{QDRANT_URL=$$QDRANT_URL,QDRANT_API_KEY=$$QDRANT_API_KEY,COLLECTION_NAME=$$COLLECTION_NAME,GOOGLE_API_KEY=$$GOOGLE_API_KEY,FASTEMBED_CACHE=$$FASTEMBED_CACHE}"
