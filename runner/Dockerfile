FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt requirements.txt
COPY sdk/python-sdk/src/requirements.txt sdk_requirements.txt

RUN pip install --no-cache-dir -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir -r sdk_requirements.txt -f https://download.pytorch.org/whl/torch_stable.html

RUN yum -y install mesa-libGL
RUN yum -y install libgomp

# Copy the SDK code we need (not all of it)
COPY sdk/python-sdk/src/feather/ ${LAMBDA_TASK_ROOT}/feather/
ENV PYTHONPATH "${LAMBDA_TASK_ROOT}/feather/"

# Copy function code
COPY app/* ${LAMBDA_TASK_ROOT}

ENV FEATHER_SERVICE_RUNNER "true"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]
