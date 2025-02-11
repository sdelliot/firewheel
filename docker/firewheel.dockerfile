FROM ghcr.io/sandia-minimega/minimega/minimega:master AS minimega

# --#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#-- #

## Package dependencies
ENV MM_INSTALL_DIR=/opt/minimega
ENV MINIMEGA_CONFIG=/etc/default/minimega
ENV MM_BASE=/tmp/minimega
ENV USER=root
ENV GRPC_HOSTNAME=localhost
ENV EXPERIMENT_INTERFACE=lo

# Install dependencies
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update && apt-get upgrade -y \
    && apt-get install -y sudo git git-lfs build-essential tar net-tools procps tmux \
                          ethtool libpcap-dev openvswitch-switch qemu-kvm qemu-utils \
                          dnsmasq ntfs-3g iproute2 qemu-system-x86 software-properties-common \
                          dosfstools openssh-server locales locales-all python3.10 python3.10-venv \
                          vim psmisc

### Locale support ###
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
RUN localedef -i en_US -f UTF-8 en_US.UTF-8
RUN echo "LANG=\"en_US.UTF-8\"" > /etc/locale.conf
### Locale Support END ###


# --#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#-- #

WORKDIR /
# Install discovery
RUN wget https://github.com/mitchnegus/minimega-discovery/releases/download/firewheel-debian_faed761/discovery.deb && \
    dpkg -i discovery.deb && \
    rm discovery.deb
RUN cd /usr/local/bin && for x in /opt/discovery/bin/*; do echo $x ; ln -s $x .; done

# --#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#-- #

## Firewheel installation
RUN bash -c "python3.10 -m venv /fwpy \
    && source /fwpy/bin/activate \
    && python3 -m pip install --upgrade wheel setuptools pip \
    && python3 -m pip install --upgrade firewheel \
    && ln -s /fwpy/bin/firewheel /usr/local/bin/firewheel"


RUN bash -c "source /fwpy/bin/activate  && \
    mkdir -p /var/log/minimega && \
    mkdir -p /scratch/firewheel && \
    firewheel config set -s system.default_group root && \
    firewheel config set -s minimega.experiment_interface lo && \
    firewheel config set -s system.default_output_dir /scratch/firewheel && \
    firewheel config set -s minimega.base_dir /tmp/minimega && \
    firewheel config set -s minimega.files_dir /tmp/minimega/files && \
    firewheel config set -s python.venv /fwpy && \
    firewheel config set -s python.bin python3 && \
    firewheel config set -s logging.root_dir /scratch/firewheel"

# Set up Bash completion
RUN bash -c "source /fwpy/bin/activate  && \
    prep_fw_tab_completion && \
    completion_script=\$(/fwpy/bin/prep_fw_tab_completion --print-path) && \
    env && \
    cp \$completion_script /usr/share/bash-completion/completions/firewheel"

# Add some supported model components
RUN bash -c "source /fwpy/bin/activate  && \
    python3 -m pip install --upgrade firewheel-repo-base firewheel-repo-linux firewheel-repo-vyos firewheel-repo-layer2 firewheel-repo-tutorials firewheel-repo-dns firewheel-repo-ntp"

RUN firewheel repository install -s -i

RUN cp /usr/bin/ssh /usr/bin/ssh-old && \
    cp /usr/bin/scp /usr/bin/scp-old && \
    cp /usr/bin/sudo /usr/bin/sudo-old && \
    cp /usr/bin/chgrp /usr/bin/chgrp-old

COPY docker/fsroot/ /
RUN chmod +x /usr/local/bin/entry && \
    chmod +x /usr/bin/ssh && \
    chmod +x /usr/bin/scp && \
    chmod +x /usr/bin/sudo && \
    chmod +x /usr/bin/chgrp && \
    chmod +x /start-minimega.sh

# --#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#-- #

ENTRYPOINT ["/usr/local/bin/entry"]
