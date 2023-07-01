#------------------------------------------------------------------------------
# Feather SDK
# Proprietary and confidential
# Unauthorized copying of this file, via any medium is strictly prohibited
# 
# (c) Feather - All rights reserved
#------------------------------------------------------------------------------
import sys
import json
import boto3
import botocore
import tempfile
import hooks
import os
import traceback
import feather
from feather.featherservice import executor

## BOOTUP - Code here is run once, on first invocation

# Connect to S3 - we do this here, and re-use it accross invocations of the lambda
session = boto3.Session(aws_access_key_id=os.environ.get("FTR_S3_ACCESS_KEY_ID"), 
    aws_secret_access_key=os.environ.get("FTR_S3_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("FTR_S3_REGION"),
    )

gS3Client = boto3.client("s3", 
    region_name=os.environ.get("FTR_S3_REGION"), 
    aws_access_key_id=os.environ.get("FTR_S3_ACCESS_KEY_ID"), 
    aws_secret_access_key=os.environ.get("FTR_S3_SECRET_ACCESS_KEY"),
    config=botocore.config.Config(s3={'addressing_style':'path'}))

gBucketName = os.environ.get("FTR_S3_BUCKET_NAME")
print("Connected to S3:", gS3Client)

class JsonObject:
    def toJSON(self, pretty=True):
        index = None if pretty == False else 4
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=index)

    def fromJSON(self, str):
        self.__dict__ = json.loads(str)

# Lambda entry point
#
# request (event):
# {
#   "id": "id of the system",
#   "definition": {
#       The system definition
#   },
#   "files": {
#       "code_files": [
#           {
#               "filename": "relative local path",
#               "s3url": "path to object on S3"
#           }
#       ],
#       "model_files": []
#   },
#   "input_data": {
#   }
# }

gCachedContext = {}

def handler(event, context):
    try:
        reqId = event["id"]
        print("FTR: New request ID=", reqId)

        if reqId in gCachedContext:
            # Context already cached, so re-use it
            # :TODO: We can cache locally the contents in rootDir  - if we get another invocation for this systemID,
            # we can re-use the files we've already loaded
            ""

        savedWorkingDir = os.getcwd()
        with tempfile.TemporaryDirectory() as rootDir:
            # Parse the request

            os.chdir(rootDir)

            # :TODO: Handle data files
            stepToRun, definition, code_files, data_files, input_data = loadRequest(event, rootDir)
            
            # Load the code...

            engine = executor.SystemExecutor(reqId, definition, code_files, rootDir)
            outputs = engine.run_step(stepToRun, input_data)
            engine.unload_modules()

            print("FTR: OK")
            # Generate the response
            ret = JsonObject()
            ret.result = 200
            ret.outputs = outputs

            # Restore cwd
            os.chdir(savedWorkingDir)
            return ret.toJSON(pretty=False)
    except Exception as e:
        os.chdir(savedWorkingDir)
        
        errMsg = "{0}, {1}".format(e.__doc__ , e.args)
        print("FTR: ERROR:", errMsg)
        traceback.print_exc()
        ret = JsonObject()
        ret.result = 400
        ret.error = errMsg
        ret.stack_trace = traceback.format_exc()
        return ret.toJSON(pretty=False)

# Given a pull path, create the directory tree if it doesn't exist
def createDirIfNeeded(filepath):
    seperator = filepath.rfind("/")
    if seperator != -1:
        subDir = filepath[:seperator]
        if os.path.exists(subDir) == False:
            os.makedirs(subDir)

# Load all the info from an incoming request - For any external files
# specified, load them from S3
def loadRequest(event, rootDir):
    hooks.feather_clear_hooks()

    request = event
    definition = request["definition"]
    files = request["files"]
    stepToRun = request["step_to_run"]

    #  Get the input data
    input_data = []
    stepName = stepToRun

    if stepToRun == "#system": 
        stepName = definition["steps"][0]["name"]

    for data in request["input_data"][stepName]:
        input_data.append(data)

    code_files = []
    data_files = []

    # Code files, we need to load and save since they  are needed to run the sytem
    for file  in files["code_files"]:
        filename = file["filename"]
        s3Url = file["s3Url"]
        destinationFile = rootDir + "/" + filename
        print("Downloading code file", filename, "from", s3Url, "to", destinationFile)
        createDirIfNeeded(destinationFile)
        
        #gS3Bucket.download_file(s3Url, destinationFile)
        gS3Client.download_file(gBucketName, s3Url, destinationFile)
        code_files.append(filename)

    # Data files, we load on demand
    for file in files["model_files"]:
        filename = file["filename"]
        s3Url = file["s3Url"]
        destinationFile = rootDir + "/" + filename
        print("Downloading data file {0} from {1} to {2}".format(filename, s3Url, destinationFile))
        createDirIfNeeded(destinationFile)

        gS3Client.download_file(gBucketName, s3Url, destinationFile)
        data_files.append(filename)

    return [stepToRun, definition, code_files, data_files, input_data]

