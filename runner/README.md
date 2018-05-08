# Setup to run Kaggle scripts on Rhino group server (rhino.csail.mit.edu)

1. Install Vagrant
    ```
    sudo apt-get install vagrant
    ```
2. Install vagrant disk-size plugin
    ```
    sudo vagrant plugin install vagrant-disksize
    ```
3. Clone the main repository to `/raid/` on Rhino (make sure nothing uses AFS)

4. Make sure that any data you want to run on is stored in
   `transfer-cleaning/runner/program_data`.
   The directory structure assumed is:
   ```
program_data
└── <project_name>
    ├── input
    │   └── <data>.csv
    └── scripts
        ├── <script>.py
        ├── ...
```

This directory is copied on to the VM and then the Docker container within that.

5. Build the vagrant VM, used to sandbox the Kaggle scripts
    ```
    cd transfer-cleaning/runner; make build_vagrant; vagrant halt
    ```
6. Start up the VM with `longjob` to remain logged in for a day (change this for longer)
    ```
    longjob --renew 1d
    ```
7. Connect to the VM
    ```
    vagrant ssh
    ```
8. Build docker inside the VM
    ```
    cd transfer-cleaning/runner; make build_docker
    ```
Note that you do not need to run the `make` command here using `sudo`, as `make build_vagrant` has already
added the default user (`vagrant`) to the `docker` group.
So all `docker` commands can run without `sudo`.

9. You can now schedule jobs to running by using the command below
    and modifying script locations etc as desired.
    The actual scheduling is done with the `at`
    command underneath the covers. Timeout is
    implemented with the `timeout` command.
    The memory limit is handed directly to the
    docker container that executes each job.

```
python schedule_jobs.py \
    cleaning \
    program_data/loan_data/scripts \
    program_data/loan_data/results \
    program_data/loan_data/results/ \
    --mem_limit 20GB \
    --timeout 2h
```

Note that if you have already built the VM with all the data needed, and docker has been built accordingly, then
you can just skip to the last step directly.

This runs with the default `atd` settings. If you want to schedule jobs so
that more are run concurrently and there is less startup time between jobs
you should:

* Find the currently running `atd` daemon.
```
ps aux | grep atd
```
* Kill it.
* Start a new `atd` daemon with your desired configuration
```
sudo atd -l <load-limit> -b <time-between-job-launches>
```
* Run `schedule_jobs.py` as explained above.


# Known Issues

* It seems that on occasion, `vagrant` can fail when building and not actually include docker. If this happens, I suggest removing the box (`vagrant destroy`), cleaning up, and calling `make build_vagrant` again. That seems to solve the issue in all cases I've encountered.

* If anything hangs for a long time, I suggest deleting the `.vagrant*`
folders created in the `transfer-cleaning/runner` folder. You may also want
to delete the `/raid/jcamsan/virtualbox_vms` folder as well. Also, kill any
`vboxmanage` or `vagrant` processes and then try again. I realize this may be
overkill (no pun intended) but not sure how to fix otherwise.