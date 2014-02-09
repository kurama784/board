# INTRO #

The API is provided to query the data from a neaboard server by any client
application.

Tha data is returned in the json format and got by an http query.

# METHODS #

## Threads ##

    /api/threads/N/?offset=M&tag=O

Get a thread list. You will get ``N`` threads (required parameter) starting from
``M``th one (optional parameter, default is 0) with the tag ``O`` (optional parameter,
threads with any tags are shown by default).

## Tags ##

    /api/tags/

Get all active tag list. Active tag is a tag that has at least 1 active thread
associated with it.

## Thread ##

    /api/thread/N/

Get all ``N``th thread post. ``N`` is an opening post ID for the thread.

Output format:

* ``posts``: list of posts
* ``last_update``: last update timestamp

## Thread diff ##

    /api/diff_thread/N/M/?type=O

Get the diff of the thread with id=``N`` from the ``M`` timestamp in the ``O`` 
format. 2 formats are available: ``html`` (used in AJAX thread update) and 
``json``. The default format is ``html``. Return list format:

* ``added``: list of added posts
* ``updated``: list of updated posts
* ``last_update``: last update timestamp

## General info ##

In case of incorrect request you can get http error 404.

Response JSON for a post or thread contains:

* ``id``
* ``title``
* ``text``
* ``image`` (if image available)
* ``image_preview`` (if image available)
* ``bump_time`` (for threads)

In future, it will also contain:

* tags list (for thread)
* publishing time
* bump time
* reply IDs (if available)
