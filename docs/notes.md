# Notes

TL;DR: architect does not seem as polished as serverless, nor does it
seem that non Javascript languages are first class citizens.

## Installation

### Failed on macos

    $ brew install npm
    ...
    Pouring node-12.10.0.mojave.bottle.tar.gz

    $ npm install -g @architect/architect
    ...
    ../src/batch.cc:91:3: error: no matching member function for call to 'ToObject'
    LD_STRING_OR_BUFFER_TO_SLICE(key, keyBuffer, key)
    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ...
    fatal error: too many errors emitted, stopping now [-ferror-limit=]
    7 warnings and 20 errors generated.
    make: *** [Release/obj.target/leveldown/src/batch.o] Error 1

### Works using docker

At least `arc init` works

## Development

The [project layout](https://arc.codes/quickstart/layout) page says
that shared code should go into `src/shared`, but when running `arc
sandbox` that path is not added to `PYTHONPATH`.  Looks like maybe
you're supposed to modify `sys.path` manually, which seems like a
pretty big code smell to me.

Looks like the body of the request is Base64 encoded.  The
documentation mentions helpers for decoding it, but only for Javascript.

The [section for testing python](https://arc.codes/guides/testing) is
empty.  Truss likes to use pytest, but the directory layout of
architect doesn't seem to fit any of the recommended [directory
layouts for
pytest](http://doc.pytest.org/en/latest/goodpractices.html).  Thus, in
the tests we also have to set up `sys.path` manually.

It's nice that logging to stdout/stderr works in architect when
running locally, unlike with serverless which confuses the logs with
the output of the lambda.

Our standard pre-commit flake8 checks fail with E402 because of the
`sys.path` manipulation.  I added that to the ignored errors in `setup.cfg`.

## Deployment

Arc doesn't support using a `Pipfile` directly, so you have run
`pipenv lock -r`.

Running `arc package` results in

    ✓ Successfully created sam.json! Now deploy it by following these steps:

    1.) Package code with SAM:
    sam package --template-file sam.json --output-template-file
    out.yaml --s3-bucket [S3 bucket]

    2.) Deploy the CloudFormation stack:
    sam deploy --template-file out.yaml --stack-name [Stack Name]
    --s3-bucket [S3 bucket] --capabilities CAPABILITY_IAM

So it looks like it's using the [aws
sam](https://docs.aws.amazon.com/lambda/latest/dg/serverless_app.html)
tool under the hood.

Run `arc deploy` results in

    ...
    Unable to upload artifact ./src/http/post-events referenced by
    CodeUri parameter of PostEvents resource.
    S3 Bucket does not exist. Execute the command to create a new bucket
    aws s3 mb s3://slackbot-architect-experiment
    deploy failed!

That's possibly a safer default, but it is slightly more friction.

Trying again after creating the bucket:

    Uploading to cbba0d540304e6ce59dcbdf09e8b4625  1811 / 1811.0  (100.00%)
    Unable to upload artifact ./src/http/get-index referenced by
    CodeUri parameter of GetIndex resource.
    Parameter CodeUri of resource GetIndex refers to a file or folder
    that does not exist /app/src/http/get-index
    deploy failed!

It looks like `arc` always wants to have a `get-index`, even though I
don't need one and removed it from my `.arc` file.  I created an empty
folder.  It got a lot farther, but then:

    Failed to create/update the stack. Run the following command
    to fetch the list of events leading up to the failure
    aws cloudformation describe-stack-events --stack-name SlackbotStaging
    deploy failed!

That seems to be because of the empty `get-index` folder.  I created
an empty `index.py` in `get-index` and now have:

    An error occurred (ValidationError) when calling the
    CreateChangeSet operation:
    Stack:arn:aws:cloudformation:us-east-1:867136165464:stack/SlackbotStaging/c25a9530-d7f0-11e9-a648-12f8925a37c4
    is in ROLLBACK_COMPLETE state and can not be updated.
    deploy failed!

I went into the aws console and deleted the cloudformation stack.  Next
I created an `index.py` with a basic handler and re-deployed and it
worked.

I was pretty excited by the `arc logs` command, but it doesn't seem to
work for the `post-events` I created.

    logs failed! The specified log group does not exist.
    ResourceNotFoundException: The specified log group does not exist.

I can't seem to find any documentation about using `arc` to remove the
deployment.
