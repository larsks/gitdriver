## Synopsis

    gitdriver.py [-h] [--config CONFIG] [--text] [--html] docid

## Options

- `--config CONFIG`, `-f CONFIG` -- path to configuration file
- `--text`, `-T` -- fetch plain text content (Look out for BOM)
- `--html`, `-H` -- fetch HTML content
- `--mime-type` -- specify arbitrary mime type

## Example usage:

    $ python gitdriver.py 1j6Ygv0_this_is_a_fake_document_id_a8Q66mvt4
    Create repository "Untitled"
    Initialized empty Git repository in /home/lars/projects/gitdriver/Untitled/.git/
    [master (root-commit) 27baec9] revision from 2013-01-08T21:57:38.837Z
     1 file changed, 1 insertion(+)
     create mode 100644 content
    [master 132175a] revision from 2013-01-08T21:57:45.800Z
     1 file changed, 1 insertion(+), 1 deletion(-)
    [master eb2302c] revision from 2013-01-09T01:47:29.593Z
     1 file changed, 5 insertions(+), 1 deletion(-)
    $ ls Untiled
    content
    $ cd Untitled
    $ git log --oneline
    d41ad6e revision from 2013-01-09T01:47:29.593Z
    8d3e3ec revision from 2013-01-08T21:57:45.800Z
    ccc0bdd revision from 2013-01-08T21:57:38.837Z

## Google setup

You will need to create an OAuth client id and secret for use with
this application, the Drive API [Python quickstart][] has links to the
necessary steps.

[python quickstart]: https://developers.google.com/drive/v3/web/quickstart/python

## Configuration

In order to make this go you will need to create file named `gd.conf`
where the code can find it (typically the directory in which you're
running the code, but you can also use the `-f` command line option to
specify an alternate location).

The file is a simple YAML document that should look like this:

    googledrive:
      client id: YOUR_CLIENT_ID
      client secret: YOUR_CLIENT_SECRET

Where `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` are replaced with the
appropriate values from Google that you established in the previous
step.

