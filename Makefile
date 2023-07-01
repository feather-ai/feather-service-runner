LOCAL_IMAGE_NAME=feather-runner

runner/sdk:
	mkdir -p runner/sdk && cd runner/sdk && git clone github-rigapaul:feather-ai/python-sdk.git 

sdk: runner/sdk
	cd runner/sdk/python-sdk && git pull

build: sdk
	cd runner && docker build . -t $(LOCAL_IMAGE_NAME)

run:
	. .local/cloud.env && docker run --rm -it -p 9000:8080 -e FTR_S3_ACCESS_KEY_ID -e FTR_S3_SECRET_ACCESS_KEY -e FTR_S3_REGION -e FTR_S3_BUCKET_NAME feather-runner

test:
	cd runner/tmp && python3 testModule.py

exampleComponents:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d @examples/example2.json

simpleClassification:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d @examples/simpleImageClassification.json

deploy: build
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 483384053975.dkr.ecr.us-east-2.amazonaws.com
	docker tag $(LOCAL_IMAGE_NAME):latest 483384053975.dkr.ecr.us-east-2.amazonaws.com/generic_runner:latest
	docker push 483384053975.dkr.ecr.us-east-2.amazonaws.com/generic_runner:latest
