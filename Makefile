build_layer:
	./aws/1-install.sh
	./aws/2-package.sh
	rm -rf create_layer/
	rm -rf python/

publish_layer:
	echo "Publishing the layer"
