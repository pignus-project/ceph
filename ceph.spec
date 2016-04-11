# vim: set noexpandtab ts=8 sw=8 :
%bcond_with ocf
%bcond_without cephfs_java
%bcond_with tests
%bcond_without tcmalloc
%bcond_without libs_compat
%bcond_with lowmem_builder
%if 0%{?fedora} || 0%{?rhel}
%bcond_with selinux
%endif
%if 0%{?suse_version}
%bcond_with selinux
%endif


%if (0%{?el5} || (0%{?rhel_version} >= 500 && 0%{?rhel_version} <= 600))
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if %{with selinux}
# get selinux policy version
%{!?_selinux_policy_version: %global _selinux_policy_version %(sed -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp 2>/dev/null || echo 0.0.0)}

%define relabel_files() \
restorecon -R /usr/bin/ceph-mon > /dev/null 2>&1; \
restorecon -R /usr/bin/ceph-osd > /dev/null 2>&1; \
restorecon -R /usr/bin/ceph-mds > /dev/null 2>&1; \
restorecon -R /usr/bin/radosgw > /dev/null 2>&1; \
restorecon -R /etc/rc\.d/init\.d/ceph > /dev/null 2>&1; \
restorecon -R /etc/rc\.d/init\.d/radosgw > /dev/null 2>&1; \
restorecon -R /var/run/ceph > /dev/null 2>&1; \
restorecon -R /var/lib/ceph > /dev/null 2>&1; \
restorecon -R /var/log/ceph > /dev/null 2>&1;
%endif

%{!?_udevrulesdir: %global _udevrulesdir /lib/udev/rules.d}

# Use systemd files on RHEL 7 and above and in SUSE/openSUSE.
# Note: We don't install unit files for the services yet. For now,
# the _with_systemd variable only implies that we'll install
# /etc/tmpfiles.d/ceph.conf in order to set up the socket directory in
# /var/run/ceph.
%if 0%{?fedora} || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1210
%global _with_systemd 1
%endif

# LTTng-UST enabled on Fedora, RHEL 6, and SLES 12
%if 0%{?fedora} || 0%{?rhel} == 6 || 0%{?suse_version} == 1315
%global _with_lttng 1
%endif

#################################################################################
# common
#################################################################################
Name:		ceph
Version:	9.2.0
Release:	5%{?dist}
Epoch:		1
Summary:	User space components of the Ceph file system
License:	LGPL-2.1 and CC-BY-SA-1.0 and GPL-2.0 and BSL-1.0 and GPL-2.0-with-autoconf-exception and BSD-3-Clause and MIT
%if 0%{?suse_version}
Group:         System/Filesystems
%endif
URL:		http://ceph.com/
Source0:	http://ceph.com/download/%{name}-%{version}.tar.bz2
%if 0%{?fedora} || 0%{?rhel}
Patch0:		init-ceph.in-fedora.patch
%endif
Patch1:		0001-Disable-erasure_codelib-neon-build.patch
# Upstream commit 1c2831a2, fixes RHBZ#1319483
Patch2:         0001-common-Cycles-Do-not-initialize-Cycles-globally.patch
#################################################################################
# dependencies that apply across all distro families
#################################################################################
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Requires:	ceph-common = %{epoch}:%{version}-%{release}
%if 0%{with selinux}
Requires:	ceph-selinux = %{epoch}:%{version}-%{release}
%endif
Requires:	python-rados = %{epoch}:%{version}-%{release}
Requires:	python-rbd = %{epoch}:%{version}-%{release}
Requires:	python-cephfs = %{epoch}:%{version}-%{release}
Requires:	python
Requires:	python-requests
Requires:	grep
Requires:	xfsprogs
Requires:	logrotate
Requires:	parted
Requires:	util-linux
Requires:	hdparm
Requires:	cryptsetup
Requires:	findutils
Requires:	which
Requires(post):	binutils
%if 0%{with cephfs_java}
BuildRequires:	java-devel
BuildRequires:	sharutils
%endif
%if 0%{with selinux}
BuildRequires:	checkpolicy
BuildRequires:	selinux-policy-devel
BuildRequires:	/usr/share/selinux/devel/policyhelp
%endif
BuildRequires:	gcc-c++
BuildRequires:	boost-devel
BuildRequires:  cmake
BuildRequires:	cryptsetup
BuildRequires:	fuse-devel
BuildRequires:	gdbm
BuildRequires:	hdparm
BuildRequires:	leveldb-devel > 1.2
BuildRequires:	libaio-devel
BuildRequires:	libcurl-devel
BuildRequires:	libedit-devel
BuildRequires:	libxml2-devel
BuildRequires:	libblkid-devel >= 2.17
BuildRequires:	libudev-devel
BuildRequires:	libtool
BuildRequires:	make
BuildRequires:	parted
BuildRequires:	perl
BuildRequires:	pkgconfig
BuildRequires:	python
BuildRequires:	python-nose
BuildRequires:	python-requests
BuildRequires:	python-virtualenv
BuildRequires:	snappy-devel
BuildRequires:	util-linux
BuildRequires:	xfsprogs
BuildRequires:	xfsprogs-devel
BuildRequires:	xmlstarlet
BuildRequires:	yasm

#################################################################################
# distro-conditional dependencies
#################################################################################
%if 0%{?suse_version}
%if 0%{?_with_systemd}
BuildRequires:  pkgconfig(systemd)
BuildRequires:	systemd-rpm-macros
%{?systemd_requires}
%endif
PreReq:		%fillup_prereq
Requires:	python-Flask
BuildRequires:	net-tools
BuildRequires:	libbz2-devel
%if 0%{?suse_version} > 1210
Requires:	gptfdisk
%if 0%{with tcmalloc}
BuildRequires:	gperftools-devel
%endif
%else
Requires:	scsirastools
BuildRequires:	google-perftools-devel
%endif
BuildRequires:	mozilla-nss-devel
BuildRequires:	keyutils-devel
BuildRequires:	libatomic-ops-devel
%else
%if 0%{?_with_systemd}
Requires:	systemd
%endif
BuildRequires:  bzip2-devel
BuildRequires:	nss-devel
BuildRequires:	keyutils-libs-devel
BuildRequires:	libatomic_ops-devel
Requires:	gdisk
Requires(post):	chkconfig
Requires(preun):	chkconfig
Requires(preun):	initscripts
%ifnarch s390 s390x
BuildRequires:	gperftools-devel
%endif
Requires:	python-flask
%endif
# boost
%if 0%{?fedora} || 0%{?rhel} 
BuildRequires:  boost-random
%endif
# python-argparse for distros with Python 2.6 or lower
%if (0%{?rhel} && 0%{?rhel} <= 6) || (0%{?suse_version} && 0%{?suse_version} <= 1110)
BuildRequires:	python-argparse
%endif
# lttng and babeltrace for rbd-replay-prep
%if 0%{?_with_lttng}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	lttng-ust-devel
BuildRequires:	libbabeltrace-devel
%endif
%if 0%{?suse_version}
BuildRequires:	lttng-ust-devel
BuildRequires:  babeltrace-devel
%endif
%endif
# expat and fastcgi for RGW
%if 0%{?suse_version}
BuildRequires:	libexpat-devel
BuildRequires:	FastCGI-devel
%endif
%if 0%{?rhel} || 0%{?fedora}
BuildRequires:	expat-devel
BuildRequires:	fcgi-devel
%endif
# python-sphinx
%if 0%{?rhel} > 0 && 0%{?rhel} < 7
BuildRequires:	python-sphinx10
%endif
%if 0%{?fedora} || 0%{?suse_version} || 0%{?rhel} >= 7
BuildRequires:	python-sphinx
%endif

%description
Ceph is a massively scalable, open-source, distributed storage system that runs
on commodity hardware and delivers object, block and file system storage.


#################################################################################
# packages
#################################################################################
%package -n ceph-common
Summary:	Ceph Common
Group:		System Environment/Base
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	python-rados = %{epoch}:%{version}-%{release}
Requires:	python-rbd = %{epoch}:%{version}-%{release}
Requires:	python-cephfs = %{epoch}:%{version}-%{release}
Requires:	python-requests
%if 0%{?_with_systemd}
%{?systemd_requires}
%endif
%if 0%{?suse_version}
Requires(pre):	pwdutils
%endif
# python-argparse is only needed in distros with Python 2.6 or lower
%if (0%{?rhel} && 0%{?rhel} <= 6) || (0%{?suse_version} && 0%{?suse_version} <= 1110)
Requires:	python-argparse
%endif
%description -n ceph-common
Common utilities to mount and interact with a ceph storage cluster.

%package fuse
Summary:	Ceph fuse-based client
Group:		System Environment/Base
Requires:	%{name}
%description fuse
FUSE based client for Ceph distributed network file system

%package -n rbd-fuse
Summary:	Ceph fuse-based client
Group:		System Environment/Base
Requires:	%{name}
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	librbd1 = %{epoch}:%{version}-%{release}
%description -n rbd-fuse
FUSE based client to map Ceph rbd images to files

%package radosgw
Summary:	Rados REST gateway
Group:		Development/Libraries
Requires:	ceph-common = %{epoch}:%{version}-%{release}
%if 0%{with selinux}
Requires:	ceph-selinux = %{epoch}:%{version}-%{release}
%endif
Requires:	librados2 = %{epoch}:%{version}-%{release}
%if 0%{?rhel} || 0%{?fedora}
Requires:	mailcap
%endif
%description radosgw
This package is an S3 HTTP REST gateway for the RADOS object store. It
is implemented as a FastCGI module using libfcgi, and can be used in
conjunction with any FastCGI capable web server.

%if %{with ocf}
%package resource-agents
Summary:	OCF-compliant resource agents for Ceph daemons
Group:		System Environment/Base
License:	LGPL-2.0
Requires:	%{name} = %{epoch}:%{version}
Requires:	resource-agents
%description resource-agents
Resource agents for monitoring and managing Ceph daemons
under Open Cluster Framework (OCF) compliant resource
managers such as Pacemaker.
%endif

%package -n librados2
Summary:	RADOS distributed object store client library
Group:		System Environment/Libraries
License:	LGPL-2.0
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{epoch}:%{version}-%{release}
%endif
%description -n librados2
RADOS is a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to access the distributed object
store using a simple file-like interface.

%package -n librados2-devel
Summary:	RADOS headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n librados2-devel
This package contains libraries and headers needed to develop programs
that use RADOS object store.

%package -n python-rados
Summary:	Python libraries for the RADOS object store
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
Obsoletes:	python-ceph < %{epoch}:%{version}-%{release}
%description -n python-rados
This package contains Python libraries for interacting with Cephs RADOS
object store.

%package -n libradosstriper1
Summary:	RADOS striping interface
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
%description -n libradosstriper1
Striping interface built on top of the rados library, allowing
to stripe bigger objects onto several standard rados objects using
an interface very similar to the rados one.

%package -n libradosstriper1-devel
Summary:	RADOS striping interface headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	libradosstriper1 = %{epoch}:%{version}-%{release}
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n libradosstriper1-devel
This package contains libraries and headers needed to develop programs
that use RADOS striping interface.

%package -n librbd1
Summary:	RADOS block device client library
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librados2 = %{epoch}:%{version}-%{release}
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{epoch}:%{version}-%{release}
%endif
%description -n librbd1
RBD is a block device striped across multiple distributed objects in
RADOS, a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to manage these block devices.

%package -n librbd1-devel
Summary:	RADOS block device headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n librbd1-devel
This package contains libraries and headers needed to develop programs
that use RADOS block device.

%package -n python-rbd
Summary:	Python libraries for the RADOS block device
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	python-rados = %{epoch}:%{version}-%{release}
Obsoletes:	python-ceph < %{epoch}:%{version}-%{release}
%description -n python-rbd
This package contains Python libraries for interacting with Cephs RADOS
block device.

%package -n libcephfs1
Summary:	Ceph distributed file system client library
Group:		System Environment/Libraries
License:	LGPL-2.0
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{epoch}:%{version}-%{release}
Obsoletes:	ceph-libcephfs
%endif
%description -n libcephfs1
Ceph is a distributed network file system designed to provide excellent
performance, reliability, and scalability. This is a shared library
allowing applications to access a Ceph distributed file system via a
POSIX-like interface.

%package -n libcephfs1-devel
Summary:	Ceph distributed file system headers
Group:		Development/Libraries
License:	LGPL-2.0
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n libcephfs1-devel
This package contains libraries and headers needed to develop programs
that use Cephs distributed file system.

%package -n python-cephfs
Summary:	Python libraries for Ceph distributed file system
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Requires:	python-rados = %{epoch}:%{version}-%{release}
Obsoletes:	python-ceph < %{epoch}:%{version}-%{release}
%description -n python-cephfs
This package contains Python libraries for interacting with Cephs distributed
file system.

%package -n ceph-test
Summary:	Ceph benchmarks and test tools
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	ceph-common
Requires:	xmlstarlet
%description -n ceph-test
This package contains Ceph benchmarks and test tools.

%if 0%{with cephfs_java}

%package -n libcephfs_jni1
Summary:	Java Native Interface library for CephFS Java bindings
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	java
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
%description -n libcephfs_jni1
This package contains the Java Native Interface library for CephFS Java
bindings.

%package -n libcephfs_jni1-devel
Summary:	Development files for CephFS Java Native Interface library
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	java
Requires:	libcephfs_jni1 = %{epoch}:%{version}-%{release}
Obsoletes:	ceph-devel < %{epoch}:%{version}-%{release}
%description -n libcephfs_jni1-devel
This package contains the development files for CephFS Java Native Interface
library.

%package -n cephfs-java
Summary:	Java libraries for the Ceph File System
Group:		System Environment/Libraries
License:	LGPL-2.0
Requires:	java
Requires:	libcephfs_jni1 = %{epoch}:%{version}-%{release}
%if 0%{?el6}
Requires:	junit4
BuildRequires:	junit4
%else
Requires:       junit
BuildRequires:  junit
%endif
%description -n cephfs-java
This package contains the Java libraries for the Ceph File System.

%endif

%if 0%{with selinux}

%package selinux
Summary:	SELinux support for Ceph MON, OSD and MDS
Group:		System Environment/Base
Requires:	%{name}
Requires:	policycoreutils, libselinux-utils
Requires(post): selinux-policy-base >= %{_selinux_policy_version}, policycoreutils, gawk
Requires(postun): policycoreutils
%description selinux
This package contains SELinux support for Ceph MON, OSD and MDS. The package
also performs file-system relabelling which can take a long time on heavily
populated file-systems.

%endif

%if 0%{with libs_compat}

%package libs-compat
Summary:	Meta package to include ceph libraries
Group:		System Environment/Libraries
License:	LGPL-2.0
Obsoletes:	ceph-libs
Requires:	librados2 = %{epoch}:%{version}-%{release}
Requires:	librbd1 = %{epoch}:%{version}-%{release}
Requires:	libcephfs1 = %{epoch}:%{version}-%{release}
Provides:	ceph-libs

%description libs-compat
This is a meta package, that pulls in librados2, librbd1 and libcephfs1. It
is included for backwards compatibility with distributions that depend on the
former ceph-libs package, which is now split up into these three subpackages.
Packages still depending on ceph-libs should be fixed to depend on librados2,
librbd1 or libcephfs1 instead.

%endif

%package devel-compat
Summary:	Compatibility package for Ceph headers
Group:		Development/Libraries
License:	LGPL-2.0
Obsoletes:	ceph-devel
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	librados2-devel = %{epoch}:%{version}-%{release}
Requires:	libradosstriper1-devel = %{epoch}:%{version}-%{release}
Requires:	librbd1-devel = %{epoch}:%{version}-%{release}
Requires:	libcephfs1-devel = %{epoch}:%{version}-%{release}
%if 0%{with cephfs_java}
Requires:	libcephfs_jni1-devel = %{epoch}:%{version}-%{release}
%endif
Provides:	ceph-devel
%description devel-compat
This is a compatibility package to accommodate ceph-devel split into
librados2-devel, librbd1-devel and libcephfs1-devel. Packages still depending
on ceph-devel should be fixed to depend on librados2-devel, librbd1-devel,
libcephfs1-devel or libradosstriper1-devel instead.

%package -n python-ceph-compat
Summary:	Compatibility package for Cephs python libraries
Group:		System Environment/Libraries
License:	LGPL-2.0
Obsoletes:	python-ceph
Requires:	python-rados = %{epoch}:%{version}-%{release}
Requires:	python-rbd = %{epoch}:%{version}-%{release}
Requires:	python-cephfs = %{epoch}:%{version}-%{release}
Provides:	python-ceph
%description -n python-ceph-compat
This is a compatibility package to accommodate python-ceph split into
python-rados, python-rbd and python-cephfs. Packages still depending on
python-ceph should be fixed to depend on python-rados, python-rbd or
python-cephfs instead.

#################################################################################
# common
#################################################################################
%prep
%setup -q
%if 0%{?fedora} || 0%{?rhel}
%patch0 -p1 -b .init
%endif
%patch1 -p1 -b .neon
%patch2 -p1 -b .cycles

%build
%if 0%{with cephfs_java}
# Find jni.h
for i in /usr/{lib64,lib}/jvm/java/include{,/linux}; do
    [ -d $i ] && java_inc="$java_inc -I$i"
done
%endif

./autogen.sh

%if %{with lowmem_builder}
RPM_OPT_FLAGS="$RPM_OPT_FLAGS --param ggc-min-expand=20 --param ggc-min-heapsize=32768"
%endif
export RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/i386/i486/'`
%ifarch s390
# Decrease debuginfo verbosity to reduce memory consumption even more
export RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/-g /-g1 /'`
%endif

# This is ONLY required to workaround XFS brokenness.  When the
# following bug is fixed, you can remove this.
# https://bugzilla.redhat.com/show_bug.cgi?id=1319804
export RPM_OPT_FLAGS="-D_GNU_SOURCE $RPM_OPT_FLAGS"


%{configure}	CPPFLAGS="$java_inc" \
		--prefix=/usr \
		--localstatedir=/var \
		--sysconfdir=/etc \
%if 0%{?_with_systemd}
		--with-systemdsystemunitdir=%_unitdir \
%endif
		--docdir=%{_docdir}/ceph \
		--with-man-pages \
		--mandir="%_mandir" \
		--with-nss \
		--without-cryptopp \
		--with-debug \
%if 0%{with cephfs_java}
		--enable-cephfs-java \
%endif
%if 0%{with selinux}
		--with-selinux \
%endif
		--with-librocksdb-static=check \
%if 0%{?rhel} || 0%{?fedora}
		--with-systemd-libexec-dir=/usr/libexec/ceph \
		--with-rgw-user=root \
		--with-rgw-group=root \
%endif
%if 0%{?suse_version}
		--with-systemd-libexec-dir=/usr/lib/ceph/ \
		--with-rgw-user=wwwrun \
		--with-rgw-group=www \
%endif
		--with-radosgw \
		$CEPH_EXTRA_CONFIGURE_ARGS \
		%{?_with_ocf} \
%ifnarch s390 s390x
		%{?_with_tcmalloc} \
%else
		--without-tcmalloc \
%endif
		CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS"


make %{?_smp_mflags}


%if 0%{with tests}
%check
# run in-tree unittests
make %{?_smp_mflags} check-local

%endif



%install
make DESTDIR=$RPM_BUILD_ROOT install
find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name "*.a" -exec rm -f {} ';'
install -D src/rbdmap $RPM_BUILD_ROOT%{_sysconfdir}/ceph/rbdmap
install -D src/init-rbdmap $RPM_BUILD_ROOT%{_initrddir}/rbdmap
%if 0%{?fedora} || 0%{?rhel}
install -m 0644 -D etc/sysconfig/ceph $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ceph
%endif
%if 0%{?suse_version}
install -m 0644 -D etc/sysconfig/ceph $RPM_BUILD_ROOT%{_localstatedir}/adm/fillup-templates/sysconfig.%{name}
%endif
%if 0%{?_with_systemd}
  install -m 0644 -D systemd/ceph.tmpfiles.d $RPM_BUILD_ROOT%{_tmpfilesdir}/ceph-common.conf
  install -m 0644 -D systemd/ceph-osd@.service $RPM_BUILD_ROOT%{_unitdir}/ceph-osd@.service
  install -m 0644 -D systemd/ceph-mon@.service $RPM_BUILD_ROOT%{_unitdir}/ceph-mon@.service
  install -m 0644 -D systemd/ceph-create-keys@.service $RPM_BUILD_ROOT%{_unitdir}/ceph-create-keys@.service
  install -m 0644 -D systemd/ceph-mds@.service $RPM_BUILD_ROOT%{_unitdir}/ceph-mds@.service
  install -m 0644 -D systemd/ceph-radosgw@.service $RPM_BUILD_ROOT%{_unitdir}/ceph-radosgw@.service
  install -m 0644 -D systemd/ceph.target $RPM_BUILD_ROOT%{_unitdir}/ceph.target
  install -m 0644 -D systemd/ceph-disk@.service $RPM_BUILD_ROOT%{_unitdir}/ceph-disk@.service
  install -m 0755 -D systemd/ceph $RPM_BUILD_ROOT%{_sbindir}/rcceph
%else
  install -D src/init-ceph $RPM_BUILD_ROOT%{_initrddir}/ceph
  install -D src/init-radosgw $RPM_BUILD_ROOT%{_initrddir}/ceph-radosgw
  ln -sf ../../etc/init.d/ceph %{buildroot}/%{_sbindir}/rcceph
  ln -sf ../../etc/init.d/ceph-radosgw %{buildroot}/%{_sbindir}/rcceph-radosgw
%endif
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
install -m 0644 -D src/logrotate.conf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/ceph
chmod 0644 $RPM_BUILD_ROOT%{_docdir}/ceph/sample.ceph.conf
chmod 0644 $RPM_BUILD_ROOT%{_docdir}/ceph/sample.fetch_config

# firewall templates
%if 0%{?suse_version}
install -m 0644 -D etc/sysconfig/SuSEfirewall2.d/services/ceph-mon %{buildroot}%{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-mon
install -m 0644 -D etc/sysconfig/SuSEfirewall2.d/services/ceph-osd-mds %{buildroot}%{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-osd-mds
%endif

# udev rules
install -m 0644 -D udev/50-rbd.rules $RPM_BUILD_ROOT%{_udevrulesdir}/50-rbd.rules
install -m 0644 -D udev/60-ceph-partuuid-workaround.rules $RPM_BUILD_ROOT%{_udevrulesdir}/60-ceph-partuuid-workaround.rules

%if (0%{?rhel} && 0%{?rhel} < 7)
install -m 0644 -D udev/95-ceph-osd-alt.rules $RPM_BUILD_ROOT/lib/udev/rules.d/95-ceph-osd.rules
%else
install -m 0644 -D udev/95-ceph-osd.rules $RPM_BUILD_ROOT/lib/udev/rules.d/95-ceph-osd.rules
%endif

%if 0%{?rhel} >= 7 || 0%{?fedora} || 0%{?suse_version}
mv $RPM_BUILD_ROOT/lib/udev/rules.d/95-ceph-osd.rules $RPM_BUILD_ROOT/usr/lib/udev/rules.d/95-ceph-osd.rules
mv $RPM_BUILD_ROOT/sbin/mount.ceph $RPM_BUILD_ROOT/usr/sbin/mount.ceph
mv $RPM_BUILD_ROOT/sbin/mount.fuse.ceph $RPM_BUILD_ROOT/usr/sbin/mount.fuse.ceph
%endif

#set up placeholder directories
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ceph
%if ! 0%{?_with_systemd}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/ceph
%endif
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/ceph
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/tmp
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/mon
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/osd
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/mds
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/radosgw
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/bootstrap-osd
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/bootstrap-mds
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/ceph/bootstrap-rgw

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%if 0%{?_with_systemd}
  %if 0%{?suse_version}
    # service_add_pre and friends don't work with parameterized systemd service
    # instances, only with single services or targets, so we always pass
    # ceph.target to these macros
    %service_add_pre ceph.target
  %endif
%endif


%post
/sbin/ldconfig
%if 0%{?_with_systemd}
  %if 0%{?suse_version}
    %fillup_only
    %service_add_post ceph.target
  %endif
%else
  /sbin/chkconfig --add ceph
%endif

%preun
%if 0%{?_with_systemd}
  %if 0%{?suse_version}
    %service_del_preun ceph.target
  %endif
  # Disable and stop on removal.
  if [ $1 = 0 ] ; then
    SERVICE_LIST=$(systemctl | grep -E '^ceph-mon@|^ceph-create-keys@|^ceph-osd@|^ceph-mds@|^ceph-disk-'  | cut -d' ' -f1)
    if [ -n "$SERVICE_LIST" ]; then
      for SERVICE in $SERVICE_LIST; do
        /usr/bin/systemctl --no-reload disable $SERVICE > /dev/null 2>&1 || :
        /usr/bin/systemctl stop $SERVICE > /dev/null 2>&1 || :
      done
    fi
  fi
%else
  %if 0%{?rhel} || 0%{?fedora}
    if [ $1 = 0 ] ; then
      /sbin/service ceph stop >/dev/null 2>&1
      /sbin/chkconfig --del ceph
    fi
  %endif
%endif

%postun
/sbin/ldconfig
%if 0%{?_with_systemd}
  if [ $1 = 1 ] ; then
    # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
    # "yes". In any case: if units are not running, do not touch them.
    SYSCONF_CEPH=/etc/sysconfig/ceph
    if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
      source $SYSCONF_CEPH
    fi
    if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
      SERVICE_LIST=$(systemctl | grep -E '^ceph-mon@|^ceph-create-keys@|^ceph-osd@|^ceph-mds@|^ceph-disk-'  | cut -d' ' -f1)
      if [ -n "$SERVICE_LIST" ]; then
        for SERVICE in $SERVICE_LIST; do
          /usr/bin/systemctl try-restart $SERVICE > /dev/null 2>&1 || :
        done
      fi
    fi
  fi
%endif

#################################################################################
# files
#################################################################################
%files
%defattr(-,root,root,-)
%docdir %{_docdir}
%dir %{_docdir}/ceph
%{_docdir}/ceph/sample.ceph.conf
%{_docdir}/ceph/sample.fetch_config
%{_bindir}/cephfs
%{_bindir}/ceph-clsinfo
%{_bindir}/ceph-rest-api
%{python_sitelib}/ceph_rest_api.py*
%{_bindir}/crushtool
%{_bindir}/monmaptool
%{_bindir}/osdmaptool
%{_bindir}/ceph-run
%{_bindir}/ceph-mon
%{_bindir}/ceph-mds
%{_bindir}/ceph-objectstore-tool
%{_bindir}/ceph-osd
%{_bindir}/ceph-detect-init
%{_bindir}/librados-config
%{_bindir}/ceph-client-debug
%{_bindir}/cephfs-journal-tool
%{_bindir}/cephfs-table-tool
%{_bindir}/cephfs-data-scan
%{_bindir}/ceph-debugpack
%{_bindir}/ceph-coverage
%if 0%{?_with_systemd}
%{_unitdir}/ceph-mds@.service
%{_unitdir}/ceph-mon@.service
%{_unitdir}/ceph-create-keys@.service
%{_unitdir}/ceph-osd@.service
%{_unitdir}/ceph-radosgw@.service
%{_unitdir}/ceph-disk@.service
%{_unitdir}/ceph.target
%else
%{_initrddir}/ceph
%endif
%{_sbindir}/ceph-disk
%{_sbindir}/ceph-disk-udev
%{_sbindir}/ceph-create-keys
%{_sbindir}/rcceph
%if 0%{?rhel} >= 7 || 0%{?fedora} || 0%{?suse_version}
%{_sbindir}/mount.ceph
%else
/sbin/mount.ceph
%endif
%dir %{_libdir}/ceph
%{_libdir}/ceph/ceph_common.sh
%{_libexecdir}/ceph/ceph-osd-prestart.sh
%dir %{_libdir}/rados-classes
%{_libdir}/rados-classes/libcls_cephfs.so*
%{_libdir}/rados-classes/libcls_rbd.so*
%{_libdir}/rados-classes/libcls_hello.so*
%{_libdir}/rados-classes/libcls_numops.so*
%{_libdir}/rados-classes/libcls_rgw.so*
%{_libdir}/rados-classes/libcls_lock.so*
%{_libdir}/rados-classes/libcls_kvs.so*
%{_libdir}/rados-classes/libcls_refcount.so*
%{_libdir}/rados-classes/libcls_log.so*
%{_libdir}/rados-classes/libcls_replica_log.so*
%{_libdir}/rados-classes/libcls_statelog.so*
%{_libdir}/rados-classes/libcls_timeindex.so*
%{_libdir}/rados-classes/libcls_user.so*
%{_libdir}/rados-classes/libcls_version.so*
%dir %{_libdir}/ceph/erasure-code
%{_libdir}/ceph/erasure-code/libec_*.so*
%if 0%{?_with_lttng}
%{_libdir}/libos_tp.so*
%{_libdir}/libosd_tp.so*
%endif
%{_udevrulesdir}/60-ceph-partuuid-workaround.rules
%{_udevrulesdir}/95-ceph-osd.rules
%config %{_sysconfdir}/bash_completion.d/ceph
%config(noreplace) %{_sysconfdir}/logrotate.d/ceph
%if 0%{?fedora} || 0%{?rhel}
%config(noreplace) %{_sysconfdir}/sysconfig/ceph
%endif
%if 0%{?suse_version}
%{_localstatedir}/adm/fillup-templates/sysconfig.*
%config %{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-mon
%config %{_sysconfdir}/sysconfig/SuSEfirewall2.d/services/ceph-osd-mds
%endif
%{python_sitelib}/ceph_detect_init*
%{_mandir}/man8/ceph-deploy.8*
%{_mandir}/man8/ceph-detect-init.8*
%{_mandir}/man8/ceph-disk.8*
%{_mandir}/man8/ceph-create-keys.8*
%{_mandir}/man8/ceph-mon.8*
%{_mandir}/man8/ceph-mds.8*
%{_mandir}/man8/ceph-osd.8*
%{_mandir}/man8/ceph-run.8*
%{_mandir}/man8/ceph-rest-api.8*
%{_mandir}/man8/crushtool.8*
%{_mandir}/man8/osdmaptool.8*
%{_mandir}/man8/monmaptool.8*
%{_mandir}/man8/cephfs.8*
%{_mandir}/man8/mount.ceph.8*
%{_mandir}/man8/ceph-debugpack.8*
%{_mandir}/man8/ceph-clsinfo.8*
%{_mandir}/man8/librados-config.8*
#set up placeholder directories
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/tmp
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/mon
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/osd
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/mds
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-osd
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-mds
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-rgw
%if ! 0%{?_with_systemd}
%attr(770,ceph,ceph) %dir %{_localstatedir}/run/ceph
%endif

#################################################################################
%files -n ceph-common
%defattr(-,root,root,-)
%{_bindir}/ceph
%{_bindir}/ceph-authtool
%{_bindir}/ceph-conf
%{_bindir}/ceph-dencoder
%{_bindir}/ceph-rbdnamer
%{_bindir}/ceph-syn
%{_bindir}/ceph-crush-location
%{_bindir}/rados
%{_bindir}/rbd
%{_bindir}/rbd-replay
%{_bindir}/rbd-replay-many
%if 0%{?_with_lttng}
%{_bindir}/rbd-replay-prep
%endif
%{_bindir}/ceph-post-file
%{_bindir}/ceph-brag
%if 0%{?_with_systemd}
%{_tmpfilesdir}/ceph-common.conf
%endif
%{_mandir}/man8/ceph-authtool.8*
%{_mandir}/man8/ceph-conf.8*
%{_mandir}/man8/ceph-dencoder.8*
%{_mandir}/man8/ceph-rbdnamer.8*
%{_mandir}/man8/ceph-syn.8*
%{_mandir}/man8/ceph-post-file.8*
%{_mandir}/man8/ceph.8*
%{_mandir}/man8/rados.8*
%{_mandir}/man8/rbd.8*
%{_mandir}/man8/rbd-replay.8*
%{_mandir}/man8/rbd-replay-many.8*
%{_mandir}/man8/rbd-replay-prep.8*
%{_datadir}/ceph/known_hosts_drop.ceph.com
%{_datadir}/ceph/id_dsa_drop.ceph.com
%{_datadir}/ceph/id_dsa_drop.ceph.com.pub
%dir %{_sysconfdir}/ceph/
%dir %{_datarootdir}/ceph/
%dir %{_libexecdir}/ceph/
%config %{_sysconfdir}/bash_completion.d/rados
%config %{_sysconfdir}/bash_completion.d/rbd
%config(noreplace) %{_sysconfdir}/ceph/rbdmap
%{_initrddir}/rbdmap
%{python_sitelib}/ceph_argparse.py*
%{python_sitelib}/ceph_daemon.py*
%{_udevrulesdir}/50-rbd.rules
%attr(3770,ceph,ceph) %dir %{_localstatedir}/log/ceph/
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/

%pre -n ceph-common
CEPH_GROUP_ID=""
CEPH_USER_ID=""
%if 0%{?rhel} || 0%{?fedora}
CEPH_GROUP_ID="-g 167"
CEPH_USER_ID="-u 167"
%endif
%if 0%{?rhel} || 0%{?fedora}
%{_sbindir}/groupadd ceph $CEPH_GROUP_ID -o -r 2>/dev/null || :
%{_sbindir}/useradd ceph $CEPH_USER_ID -o -r -g ceph -s /sbin/nologin -c "Ceph daemons" -d %{_localstatedir}/lib/ceph 2> /dev/null || :
%endif
%if 0%{?suse_version}
getent group ceph >/dev/null || groupadd -r ceph
getent passwd ceph >/dev/null || useradd -r -g ceph -d %{_localstatedir}/lib/ceph -s /sbin/nologin -c "Ceph daemons" ceph
%endif
exit 0

%post -n ceph-common
%if 0%{?_with_systemd}
systemd-tmpfiles --create --prefix=/run/ceph
%endif

%postun -n ceph-common
# Package removal cleanup
if [ "$1" -eq "0" ] ; then
    rm -rf /var/log/ceph
    rm -rf /etc/ceph
fi

#################################################################################
%files fuse
%defattr(-,root,root,-)
%{_bindir}/ceph-fuse
%{_mandir}/man8/ceph-fuse.8*
%if 0%{?rhel} >= 7 || 0%{?fedora} || 0%{?suse_version}
%{_sbindir}/mount.fuse.ceph
%else
/sbin/mount.fuse.ceph
%endif

#################################################################################
%files -n rbd-fuse
%defattr(-,root,root,-)
%{_bindir}/rbd-fuse
%{_mandir}/man8/rbd-fuse.8*

#################################################################################
%files radosgw
%defattr(-,root,root,-)
%{_bindir}/radosgw
%{_bindir}/radosgw-admin
%{_bindir}/radosgw-object-expirer
%{_mandir}/man8/radosgw.8*
%{_mandir}/man8/radosgw-admin.8*
%config %{_sysconfdir}/bash_completion.d/radosgw-admin
%dir %{_localstatedir}/lib/ceph/radosgw
%if 0%{?_with_systemd}
%else
%{_initrddir}/ceph-radosgw
%{_sbindir}/rcceph-radosgw
%endif

%post radosgw
/sbin/ldconfig
%if 0%{?suse_version}
  # explicit systemctl daemon-reload (that's the only relevant bit of
  # service_add_post; the rest is all sysvinit --> systemd migration which
  # isn't applicable in this context (see above comment).
  /usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

%preun radosgw
%if 0%{?_with_systemd}
  # Disable and stop on removal.
  if [ $1 = 0 ] ; then
    SERVICE_LIST=$(systemctl | grep -E '^ceph-radosgw@'  | cut -d' ' -f1)
    if [ -n "$SERVICE_LIST" ]; then
      for SERVICE in $SERVICE_LIST; do
        /usr/bin/systemctl --no-reload disable $SERVICE > /dev/null 2>&1 || :
        /usr/bin/systemctl stop $SERVICE > /dev/null 2>&1 || :
      done
    fi
  fi
%endif

%postun radosgw
/sbin/ldconfig
%if 0%{?_with_systemd}
  if [ $1 = 1 ] ; then
    # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
    # "yes". In any case: if units are not running, do not touch them.
    SYSCONF_CEPH=/etc/sysconfig/ceph
    if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
      source $SYSCONF_CEPH
    fi
    if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
      SERVICE_LIST=$(systemctl | grep -E '^ceph-radosgw@'  | cut -d' ' -f1)
      if [ -n "$SERVICE_LIST" ]; then
        for SERVICE in $SERVICE_LIST; do
          /usr/bin/systemctl try-restart $SERVICE > /dev/null 2>&1 || :
        done
      fi
    fi
  fi
%endif

#################################################################################
%if %{with ocf}
%files resource-agents
%defattr(0755,root,root,-)
%dir /usr/lib/ocf
%dir /usr/lib/ocf/resource.d
%dir /usr/lib/ocf/resource.d/ceph
/usr/lib/ocf/resource.d/%{name}/*
%endif

#################################################################################
%files -n librados2
%defattr(-,root,root,-)
%{_libdir}/librados.so.*
%if 0%{?_with_lttng}
%{_libdir}/librados_tp.so.*
%endif

%post -n librados2
/sbin/ldconfig

%postun -n librados2
/sbin/ldconfig

#################################################################################
%files -n librados2-devel
%defattr(-,root,root,-)
%dir %{_includedir}/rados
%{_includedir}/rados/librados.h
%{_includedir}/rados/librados.hpp
%{_includedir}/rados/buffer.h
%{_includedir}/rados/page.h
%{_includedir}/rados/crc32c.h
%{_includedir}/rados/rados_types.h
%{_includedir}/rados/rados_types.hpp
%{_includedir}/rados/memory.h
%{_libdir}/librados.so
%if 0%{?_with_lttng}
%{_libdir}/librados_tp.so
%endif

#################################################################################
%files -n python-rados
%defattr(-,root,root,-)
%{python_sitelib}/rados.py*

#################################################################################
%files -n libradosstriper1
%defattr(-,root,root,-)
%{_libdir}/libradosstriper.so.*

%post -n libradosstriper1
/sbin/ldconfig

%postun -n libradosstriper1
/sbin/ldconfig

#################################################################################
%files -n libradosstriper1-devel
%defattr(-,root,root,-)
%dir %{_includedir}/radosstriper
%{_includedir}/radosstriper/libradosstriper.h
%{_includedir}/radosstriper/libradosstriper.hpp
%{_libdir}/libradosstriper.so

#################################################################################
%files -n librbd1
%defattr(-,root,root,-)
%{_libdir}/librbd.so.*
%if 0%{?_with_lttng}
%{_libdir}/librbd_tp.so.*
%endif

%post -n librbd1
/sbin/ldconfig
mkdir -p /usr/lib64/qemu/
ln -sf %{_libdir}/librbd.so.1 /usr/lib64/qemu/librbd.so.1

%postun -n librbd1
/sbin/ldconfig

#################################################################################
%files -n librbd1-devel
%defattr(-,root,root,-)
%dir %{_includedir}/rbd
%{_includedir}/rbd/librbd.h
%{_includedir}/rbd/librbd.hpp
%{_includedir}/rbd/features.h
%{_libdir}/librbd.so
%if 0%{?_with_lttng}
%{_libdir}/librbd_tp.so
%endif

#################################################################################
%files -n python-rbd
%defattr(-,root,root,-)
%{python_sitelib}/rbd.py*

#################################################################################
%files -n libcephfs1
%defattr(-,root,root,-)
%{_libdir}/libcephfs.so.*

%post -n libcephfs1
/sbin/ldconfig

%postun -n libcephfs1
/sbin/ldconfig

#################################################################################
%files -n libcephfs1-devel
%defattr(-,root,root,-)
%dir %{_includedir}/cephfs
%{_includedir}/cephfs/libcephfs.h
%{_libdir}/libcephfs.so

#################################################################################
%files -n python-cephfs
%defattr(-,root,root,-)
%{python_sitelib}/cephfs.py*

#################################################################################
%files -n ceph-test
%defattr(-,root,root,-)
%{_bindir}/ceph_bench_log
%{_bindir}/ceph_kvstorebench
%{_bindir}/ceph_multi_stress_watch
%{_bindir}/ceph_erasure_code
%{_bindir}/ceph_erasure_code_benchmark
%{_bindir}/ceph_omapbench
%{_bindir}/ceph_objectstore_bench
%{_bindir}/ceph_perf_objectstore
%{_bindir}/ceph_perf_local
%{_bindir}/ceph_perf_msgr_client
%{_bindir}/ceph_perf_msgr_server
%{_bindir}/ceph_psim
%{_bindir}/ceph_radosacl
%{_bindir}/ceph_rgw_jsonparser
%{_bindir}/ceph_rgw_multiparser
%{_bindir}/ceph_scratchtool
%{_bindir}/ceph_scratchtoolpp
%{_bindir}/ceph_smalliobench
%{_bindir}/ceph_smalliobenchdumb
%{_bindir}/ceph_smalliobenchfs
%{_bindir}/ceph_smalliobenchrbd
%{_bindir}/ceph_streamtest
%{_bindir}/ceph_test_*
%{_bindir}/ceph_tpbench
%{_bindir}/ceph_xattr_bench
%{_bindir}/ceph-monstore-tool
%{_bindir}/ceph-osdomap-tool
%{_bindir}/ceph-kvstore-tool
%dir %{_libdir}/ceph
%{_libdir}/ceph/ceph-monstore-update-crush.sh

#################################################################################
%if 0%{with cephfs_java}
%files -n libcephfs_jni1
%defattr(-,root,root,-)
%{_libdir}/libcephfs_jni.so.*

%post -n libcephfs_jni1
/sbin/ldconfig

%postun -n libcephfs_jni1
/sbin/ldconfig

#################################################################################
%files -n libcephfs_jni1-devel
%defattr(-,root,root,-)
%{_libdir}/libcephfs_jni.so

#################################################################################
%files -n cephfs-java
%defattr(-,root,root,-)
%{_javadir}/libcephfs.jar
%{_javadir}/libcephfs-test.jar
%endif

#################################################################################
%if 0%{with selinux}
%files selinux
%defattr(-,root,root,-)
%attr(0600,root,root) %{_datadir}/selinux/packages/ceph.pp
%{_datadir}/selinux/devel/include/contrib/ceph.if
%{_mandir}/man8/ceph_selinux.8*

%post selinux
# Install the policy
OLD_POLVER=$(%{_sbindir}/semodule -l | grep -P '^ceph[\t ]' | awk '{print $2}')
%{_sbindir}/semodule -n -i %{_datadir}/selinux/packages/ceph.pp
NEW_POLVER=$(%{_sbindir}/semodule -l | grep -P '^ceph[\t ]' | awk '{print $2}')

# Load the policy if SELinux is enabled
if %{_sbindir}/selinuxenabled; then
    %{_sbindir}/load_policy
else
    # Do not relabel if selinux is not enabled
    exit 0
fi

if test "$OLD_POLVER" == "$NEW_POLVER"; then
   # Do not relabel if policy version did not change
   exit 0
fi

# Check whether the daemons are running
%if 0%{?_with_systemd}
    /usr/bin/systemctl status ceph.target > /dev/null 2>&1
%else
    /sbin/service ceph status >/dev/null 2>&1
%endif
STATUS=$?

# Stop the daemons if they were running
if test $STATUS -eq 0; then
%if 0%{?_with_systemd}
    /usr/bin/systemctl stop ceph.target > /dev/null 2>&1
%else
    /sbin/service ceph stop >/dev/null 2>&1
%endif
fi

# Now, relabel the files
%relabel_files

# Start the daemons iff they were running before
if test $STATUS -eq 0; then
%if 0%{?_with_systemd}
    /usr/bin/systemctl start ceph.target > /dev/null 2>&1 || :
%else
    /sbin/service ceph start >/dev/null 2>&1 || :
%endif
fi

exit 0

%postun selinux
if [ $1 -eq 0 ]; then
    # Remove the module
    %{_sbindir}/semodule -n -r ceph

    # Reload the policy if SELinux is enabled
    if %{_sbindir}/selinuxenabled ; then
        %{_sbindir}/load_policy
    else
        # Do not relabel if SELinux is not enabled
        exit 0
    fi

    # Check whether the daemons are running
    %if 0%{?_with_systemd}
        /usr/bin/systemctl status ceph.target > /dev/null 2>&1
    %else
        /sbin/service ceph status >/dev/null 2>&1
    %endif
    STATUS=$?

    # Stop the daemons if they were running
    if test $STATUS -eq 0; then
    %if 0%{?_with_systemd}
        /usr/bin/systemctl stop ceph.target > /dev/null 2>&1
    %else
        /sbin/service ceph stop >/dev/null 2>&1
    %endif
    fi

    # Now, relabel the files
    %relabel_files

    # Start the daemons if they were running before
    if test $STATUS -eq 0; then
    %if 0%{?_with_systemd}
	/usr/bin/systemctl start ceph.target > /dev/null 2>&1 || :
    %else
	/sbin/service ceph start >/dev/null 2>&1 || :
    %endif
    fi
fi
exit 0

%endif # with selinux

#################################################################################
%if 0%{with libs_compat}
%files libs-compat
# We need an empty %%files list for ceph-libs-compat, to tell rpmbuild to actually
# build this meta package.

#################################################################################
%files devel-compat
# We need an empty %%files list for ceph-devel-compat, to tell rpmbuild to
# actually build this meta package.
%endif

#################################################################################
%files -n python-ceph-compat
# We need an empty %%files list for python-ceph-compat, to tell rpmbuild to
# actually build this meta package.

%changelog
* Mon Apr 11 2016 Richard W.M. Jones <rjones@redhat.com> - 1:9.2.0-5
- Fix large startup times of processes linking to -lrbd.
  Backport upstream commit 1c2831a2, fixes RHBZ#1319483.
- Add workaround for XFS header brokenness.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:9.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 14 2016 Jonathan Wakely <jwakely@redhat.com> - 1:9.2.0-3
- Rebuilt for Boost 1.60

* Mon Dec 14 2015 Dan Horák <dan[at]danny.cz> - 1:9.2.0-2
- fix build on s390(x) - gperftools/tcmalloc not available there

* Tue Nov 10 2015 Boris Ranto <branto@redhat.com> - 1:9.2.0-1
- Rebase to latest stable upstream version (9.2.0 - infernalis)
- Use upstream spec file

* Tue Oct 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.5-1
- Rebase to latest upstream version

* Tue Oct 20 2015 Boris Ranto <branto@redhat.com> - 1:0.94.4-1
- Rebase to latest upstream version
- The rtdsc patch got merged upstream and is already present in the release

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1:0.94.3-2
- Rebuilt for Boost 1.59

* Thu Aug 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.3-1
- Rebase to latest upstream version
- The boost patch got merged upstream and is already present in the release

* Fri Jul 31 2015 Richard W.M. Jones <rjones@redhat.com> - 1:0.94.2-4
- Fix build against boost 1.58 (http://tracker.ceph.com/issues/11576).

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.2-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 1:0.94.2-2
- rebuild for Boost 1.58

* Thu Jul 16 2015 Boris Ranto <branto@redhat.com> - 1:0.94.2-1
- Rebase to latest upstream version

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Dan Horák <dan[at]danny.cz> - 1:0.94.1-4
- fix build on s390(x) - no gperftools there

* Thu May 21 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-3
- Disable lttng support (rhbz#1223319)

* Mon May 18 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-2
- Fix arm linking issue (rhbz#1222286)

* Tue Apr 14 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-1
- Rebase to latest upstream version and sync-up the spec file
- Add arm compilation patches

* Wed Apr 01 2015 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:0.87.1-3
- add version numbers to Obsoletes (RHBZ #1193182)

* Wed Mar 4 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-2
- Perform a hardened build
- Use git-formatted patches
- Add patch for pthreads rwlock unlock problem
- Do not remove conf files on uninstall
- Remove the cleanup function, it is only necessary for f20 and f21

* Wed Feb 25 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-1
- Rebase to latest upstream
- Remove boost patch, it is in upstream tarball
- Build with yasm, tarball contains fix for the SELinux issue

* Thu Jan 29 2015 Petr Machata <pmachata@redhat.com> - 1:0.87-2
- Rebuild for boost 1.57.0
- Include <boost/optional/optional_io.hpp> instead of
  <boost/optional.hpp>.  Keep the old dumping behavior in
  osd/ECBackend.cc (ceph-0.87-boost157.patch)

* Mon Nov 3 2014 Boris Ranto <branto@redhat.com> - 1:0.87-1
- Rebase to latest major version (firefly -> giant)

* Thu Oct 16 2014 Boris Ranto <branto@redhat.com - 1:0.80.7-1
- Rebase to latest upstream version

* Sat Oct 11 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-3
- Fix a typo in librados-devel vs librados2-devel dependency

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-2
- Provide empty file list for python-ceph-compat and ceph-devel-compat

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-1
- Rebase to 0.80.6
- Split ceph-devel and python-ceph packages

* Tue Sep 9 2014 Dan Horák <dan[at]danny.cz> - 1:0.80.5-10
- update Requires for s390(x)

* Wed Sep 3 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-9
- Symlink librd.so.1 to /usr/lib64/qemu only on rhel6+ x86_64 (1136811)

* Thu Aug 21 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-8
- Revert the previous change
- Fix bz 1118504, second attempt (yasm appears to be the package that caused this
- Fix bogus dates

* Wed Aug 20 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-7
- Several more merges from file to try to fix the selinux issue (1118504)

* Sun Aug 17 2014 Kalev Lember <kalevlember@gmail.com> - 1:0.80.5-6
- Obsolete ceph-libcephfs

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-5
- Do not require xfsprogs/xfsprogs-devel for el6
- Require gperftools-devel for non-ppc*/s390* architectures only
- Do not require junit -- no need to build libcephfs-test.jar
- Build without libxfs for el6
- Build without tcmalloc for ppc*/s390* architectures
- Location of mkcephfs must depend on a rhel release
- Use epoch in the Requires fields [1130700]

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-4
- Use the proper version name in Obsoletes

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.80.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-2
- Add the arm pthread hack

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-1
- Bump the Epoch, we need to keep the latest stable, not development, ceph version in fedora
- Use the upstream spec file with the ceph-libs split
- Add libs-compat subpackage [1116546]
- use fedora in rhel 7 checks
- obsolete libcephfs [1116614]
- depend on redhat-lsb-core for the initscript [1108696]

* Wed Aug 13 2014 Kalev Lember <kalevlember@gmail.com> - 0.81.0-6
- Add obsoletes to keep the upgrade path working (#1118510)

* Mon Jul 7 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-5
- revert to old spec until after f21 branch

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- temporary exclude f21/armv7hl. N.B. it builds fine on f20/armv7hl.

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-4
- upstream ceph.spec file

* Tue Jul 1 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-3
- upstream ceph.spec file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.81.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 likewise for tcmalloc, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 does not have gperftools, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-1
- ceph-0.81.0

* Wed Jun  4 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.80.1-5
- gperftools now available on aarch64/ppc64

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 0.80.1-4
- Rebuild for boost 1.55.0

* Fri May 23 2014 David Tardon <dtardon@redhat.com> - 0.80.1-3
- rebuild for boost 1.55.0

* Wed May 14 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-2
- build epel-6
- exclude %%{_libdir}/ceph/erasure-code in base package

* Tue May 13 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-1
- Update to latest stable upstream release, BZ 1095201
- PIE, _hardened_build, BZ 955174

* Thu Feb 06 2014 Ken Dreyer <ken.dreyer@inktank.com> - 0.72.2-2
- Move plugins from -devel into -libs package (#891993). Thanks Michael
  Schwendt.

* Mon Jan 06 2014 Ken Dreyer <ken.dreyer@inktank.com> 0.72.2-1
- Update to latest stable upstream release
- Use HTTPS for URLs
- Submit Automake 1.12 patch upstream
- Move unversioned shared libs from ceph-libs into ceph-devel

* Wed Dec 18 2013 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> 0.67.3-4
- build without tcmalloc on aarch64 (no gperftools)

* Sat Nov 30 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.67.3-3
- gperftools not currently available on aarch64

* Mon Oct 07 2013 Dan Horák <dan[at]danny.cz> - 0.67.3-2
- fix build on non-x86_64 64-bit arches

* Wed Sep 11 2013 Josef Bacik <josef@toxicpanda.com> - 0.67.3-1
- update to 0.67.3

* Wed Sep 11 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.61.7-3
- let base package include all its documentation files via %%doc magic,
  so for Fedora 20 Unversioned Docdirs no files are included accidentally
- include the sample config files again (instead of just an empty docdir
  that has been added for #846735)
- don't include librbd.so.1 also in -devel package (#1003202)
- move one misplaced rados plugin from -devel into -libs package (#891993)
- include missing directories in -devel and -libs packages
- move librados-config into the -devel pkg where its manual page is, too
- add %%_isa to subpackage dependencies
- don't use %%defattr anymore
- add V=1 to make invocation for verbose build output

* Wed Jul 31 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.61.7-2
- re-enable tmalloc on arm now gperftools is fixed

* Mon Jul 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.61.7-1
- Update to 0.61.7

* Sat Jul 27 2013 pmachata@redhat.com - 0.56.4-2
- Rebuild for boost 1.54.0

* Fri Mar 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.4-1
- Update to 0.56.4
- Add upstream d02340d90c9d30d44c962bea7171db3fe3bfba8e to fix logrotate

* Wed Feb 20 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.3-1
- Update to 0.56.3

* Mon Feb 11 2013 Richard W.M. Jones <rjones@redhat.com> - 0.53-2
- Rebuilt to try to fix boost dependency problem in Rawhide.

* Thu Nov  1 2012 Josef Bacik <josef@toxicpanda.com> - 0.53-1
- Update to 0.53

* Mon Sep 24 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-3
- Fix automake 1.12 error
- Rebuild after buildroot was messed up

* Tue Sep 18 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-2
- Use system leveldb

* Fri Sep 07 2012 David Nalley <david@gnsa.us> - 0.51-1
- Updating to 0.51
- Updated url and source url. 

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.46-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  9 2012 Josef Bacik <josef@toxicpanda.com> - 0.46-1
- updated to upstream 0.46
- broke out libcephfs (rhbz# 812975)

* Mon Apr 23 2012 Dan Horák <dan[at]danny.cz> - 0.45-2
- fix detection of C++11 atomic header

* Thu Apr 12 2012 Josef Bacik <josef@toxicpanda.com> - 0.45-1
- updating to upstream 0.45

* Wed Apr  4 2012 Niels de Vos <devos@fedoraproject.org> - 0.44-5
- Add LDFLAGS=-lpthread on any ARM architecture
- Add CFLAGS=-DAO_USE_PTHREAD_DEFS on ARMv5tel

* Mon Mar 26 2012 Dan Horák <dan[at]danny.cz> 0.44-4
- gperftools not available also on ppc

* Mon Mar 26 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-3
- Remove unneeded patch

* Sun Mar 25 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-2
- Update to 0.44
- Fix build problems

* Mon Mar  5 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.43-1
- Update to 0.43
- Remove upstreamed compile fixes patch
- Remove obsoleted dump_pop patch

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.41-2
- Rebuilt for c++ ABI breakage

* Thu Feb 16 2012 Tom Callaway <spot@fedoraproject.org> 0.41-1
- update to 0.41
- fix issues preventing build
- rebuild against gperftools

* Sat Dec 03 2011 David Nalley <david@gnsa.us> 0.38-1
- updating to upstream 0.39

* Sat Nov 05 2011 David Nalley <david@gnsa.us> 0.37-1
- create /etc/ceph - bug 745462
- upgrading to 0.37, fixing 745460, 691033
- fixing various logrotate bugs 748930, 747101

* Fri Aug 19 2011 Dan Horák <dan[at]danny.cz> 0.31-4
- google-perftools not available also on s390(x)

* Mon Jul 25 2011 Karsten Hopp <karsten@redhat.com> 0.31-3
- build without tcmalloc on ppc64, BR google-perftools is not available there

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-2
- Remove curl/types.h include since we don't use it anymore

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-1
- Update to 0.31

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26-2
- Add the compile fix patch

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26
- Update to 0.26

* Tue Mar 22 2011 Josef Bacik <josef@toxicpanda.com> 0.25.1-1
- Update to 0.25.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 Steven Pritchard <steve@kspei.com> 0.21.3-1
- Update to 0.21.3.

* Mon Aug 30 2010 Steven Pritchard <steve@kspei.com> 0.21.2-1
- Update to 0.21.2.

* Thu Aug 26 2010 Steven Pritchard <steve@kspei.com> 0.21.1-1
- Update to 0.21.1.
- Sample configs moved to /usr/share/doc/ceph/.
- Added cclass, rbd, and cclsinfo.
- Dropped mkmonfs and rbdtool.
- mkcephfs moved to /sbin.
- Add libcls_rbd.so.

* Tue Jul  6 2010 Josef Bacik <josef@toxicpanda.com> 0.20.2-1
- update to 0.20.2

* Wed May  5 2010 Josef Bacik <josef@toxicpanda.com> 0.20-1
- update to 0.20
- disable hadoop building
- remove all the test binaries properly

* Fri Apr 30 2010 Sage Weil <sage@newdream.net> 0.19.1-5
- Remove java deps (no need to build hadoop by default)
- Include all required librados helpers
- Include fetch_config sample
- Include rbdtool
- Remove misc debugging, test binaries

* Fri Apr 30 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-4
- Add java-devel and java tricks to get hadoop to build

* Mon Apr 26 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-3
- Move the rados and cauthtool man pages into the base package

* Sun Apr 25 2010 Jonathan Dieter <jdieter@lesbg.com> 0.19.1-2
- Add missing libhadoopcephfs.so* to file list
- Add COPYING to all subpackages
- Fix ownership of /usr/lib[64]/ceph
- Enhance description of fuse client

* Tue Apr 20 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-1
- Update to 0.19.1

* Mon Feb  8 2010 Josef Bacik <josef@toxicpanda.com> 0.18-1
- Initial spec file creation, based on the template provided in the ceph src
