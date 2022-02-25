#!/usr/bin/env fish

# fish while: <https://fishshell.com/docs/current/cmds/while.html>
# fish read: <https://fishshell.com/docs/current/cmds/read.html>
# inotify-tools: <https://www.linuxjournal.com/content/linux-filesystem-events-inotify>

set -l watchThisFolder ./_posts/

while inotifywait --event modify $watchThisFolder | read -t arg1 arg2 arg3
    sleep 1s
    echo $arg3
    doctoc $watchThisFolder$arg3
end
