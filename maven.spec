%global homedir %{_datadir}/%{name}%{?maven_version_suffix}
%global confdir %{_sysconfdir}/%{name}%{?maven_version_suffix}

Name:              maven
Epoch:             1
Version:           3.5.4
Release:           3
Summary:           A tool can be used for building and managing any Java-based project
License:           ASL 2.0
URL:               http://maven.apache.org/
Source0:           http://archive.apache.org/dist/%{name}/%{name}-3/%{version}/source/apache-%{name}-%{version}-src.tar.gz
Source1:           maven-bash-completion
Source2:           mvn.1

Patch0000:         Revert-MNG-6335-Update-Mockito-to-2.12.0.patch

BuildRequires:     maven-local mvn(com.google.guava:guava:20.0) mvn(com.google.inject:guice::no_aop:) mvn(commons-cli:commons-cli)
BuildRequires:     mvn(commons-jxpath:commons-jxpath) mvn(javax.annotation:jsr250-api) mvn(javax.inject:javax.inject)
BuildRequires:     mvn(junit:junit) mvn(org.apache.commons:commons-lang3) mvn(org.apache.maven:maven-parent:pom:)
BuildRequires:     mvn(org.apache.maven.plugins:maven-assembly-plugin) mvn(org.apache.maven.plugins:maven-dependency-plugin)
BuildRequires:     mvn(org.apache.maven.resolver:maven-resolver-api) mvn(org.apache.maven.resolver:maven-resolver-connector-basic)
BuildRequires:     mvn(org.apache.maven.resolver:maven-resolver-impl) mvn(org.apache.maven.resolver:maven-resolver-spi)
BuildRequires:     mvn(org.apache.maven.resolver:maven-resolver-transport-wagon) mvn(org.apache.maven.resolver:maven-resolver-util)
BuildRequires:     mvn(org.apache.maven.shared:maven-shared-utils) mvn(org.apache.maven.wagon:wagon-file)
BuildRequires:     mvn(org.apache.maven.wagon:wagon-http::shaded:) mvn(org.apache.maven.wagon:wagon-provider-api)
BuildRequires:     mvn(org.codehaus.modello:modello-maven-plugin) mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires:     mvn(org.codehaus.plexus:plexus-classworlds) mvn(org.codehaus.plexus:plexus-component-annotations)
BuildRequires:     mvn(org.codehaus.plexus:plexus-component-metadata) mvn(org.codehaus.plexus:plexus-interpolation)
BuildRequires:     mvn(org.codehaus.plexus:plexus-utils) mvn(org.eclipse.sisu:org.eclipse.sisu.inject)
BuildRequires:     mvn(org.eclipse.sisu:org.eclipse.sisu.plexus) mvn(org.eclipse.sisu:sisu-maven-plugin)
BuildRequires:     mvn(org.fusesource.jansi:jansi) mvn(org.mockito:mockito-core) mvn(org.slf4j:jcl-over-slf4j)
BuildRequires:     mvn(org.slf4j:slf4j-api) mvn(org.slf4j:slf4j-simple) mvn(org.sonatype.plexus:plexus-cipher)
BuildRequires:     mvn(org.sonatype.plexus:plexus-sec-dispatcher) mvn(xmlunit:xmlunit) slf4j-sources = 1.7.25
BuildRequires:     mvn(ch.qos.logback:logback-classic)
Requires:          aopalliance apache-commons-cli apache-commons-codec apache-commons-io apache-commons-lang3
Requires:          apache-commons-logging atinject cdi-api geronimo-annotation google-guice guava20 hawtjni-runtime
Requires:          httpcomponents-client httpcomponents-core jansi jansi-native jcl-over-slf4j maven-resolver-api
Requires:          maven-resolver-connector-basic maven-resolver-impl maven-resolver-spi maven-resolver-transport-wagon
Requires:          maven-resolver-util maven-shared-utils maven-wagon-file maven-wagon-http maven-wagon-http-shared
Requires:          maven-wagon-provider-api plexus-cipher plexus-classworlds plexus-containers-component-annotations
Requires:          plexus-interpolation plexus-sec-dispatcher plexus-utils sisu-inject sisu-plexus slf4j
OrderWithRequires: xmvn-minimal
Provides:          %{name}-lib = %{epoch}:%{version}-%{release} bundled(slf4j) = 1.7.25 config(maven-lib) = %{epoch}:%{version}-%{release}
Obsoletes:         %{name}-lib < %{epoch}:%{version}-%{release}
Requires(post):    chkconfig
Requires(postun):  chkconfig
BuildArch:         noarch

%description
Apache Maven is a software project management and comprehension tool. Based on the concept of a project object
model (POM), Maven can manage a project's build, reporting and documentation from a central piece of information.

%package           help
Summary:           Help package for maven
Provides:          %{name}-javadoc = %{epoch}:%{version}-%{release}
Obsoletes:         %{name}-javadoc < %{epoch}:%{version}-%{release}

%description       help
This package conatins API and man documentation for maven.

%prep
%autosetup -n apache-%{name}-%{version} -p1

find -name '*.jar' -not -path '*/test/*' -delete
find -name '*.class' -delete
find -name '*.bat' -delete
sed -i 's:\r::' apache-maven/src/conf/settings.xml
rm apache-maven/src/main/appended-resources/META-INF/LICENSE.vm

%pom_remove_plugin -r :animal-sniffer-maven-plugin
%pom_remove_plugin -r :apache-rat-plugin
%pom_remove_plugin -r :maven-site-plugin
%pom_remove_plugin -r :buildnumber-maven-plugin
sed -i "
/buildNumber=/ {
  s/=.*/=openEuler %{version}-%{release}/
}
/timestamp=/ d
" `find -name build.properties`

%mvn_package :apache-maven __noinstall
%mvn_alias :maven-resolver-provider :maven-aether-provider

%build
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8
install -d m2home
cd m2home
tar --delay-directory-restore -xvf ../apache-maven/target/*tar.gz

%install
%mvn_install
export M2_HOME=$(pwd)/m2home/apache-maven-%{version}%{?ver_add}
install -d -m 755 %{buildroot}%{homedir}/conf %{buildroot}%{confdir} %{buildroot}%{_datadir}/bash-completion/completions/
cp -a $M2_HOME/{bin,lib,boot} %{buildroot}%{homedir}/
xmvn-subst -R %{buildroot} -s %{buildroot}%{homedir}
build-jar-repository -s -p %{buildroot}%{homedir}/lib commons-{codec,logging} httpcomponents/{httpclient,httpcore} maven-wagon/http-shared
rm %{buildroot}%{homedir}/lib/jboss-interceptors*.jar %{buildroot}%{homedir}/lib/javax.el-api*.jar
install -p -m 644 %{SOURCE2} %{buildroot}%{homedir}/bin/
gzip -9 %{buildroot}%{homedir}/bin/mvn.1
install -p -m 644 %{SOURCE1} %{buildroot}%{_datadir}/bash-completion/completions/mvn%{?maven_version_suffix}
mv $M2_HOME/bin/m2.conf %{buildroot}%{_sysconfdir}/m2%{?maven_version_suffix}.conf
ln -sf %{_sysconfdir}/m2%{?maven_version_suffix}.conf %{buildroot}%{homedir}/bin/m2.conf
mv $M2_HOME/conf/settings.xml %{buildroot}%{confdir}/
ln -sf %{confdir}/settings.xml %{buildroot}%{homedir}/conf/settings.xml
mv $M2_HOME/conf/logging %{buildroot}%{confdir}/
ln -sf %{confdir}/logging %{buildroot}%{homedir}/conf
install -d -m 755 %{buildroot}%{_bindir}/ %{buildroot}%{_mandir}/man1/
touch %{buildroot}%{_bindir}/{mvn,mvnDebug} %{buildroot}%{_mandir}/man1/{mvn,mvnDebug}.1

%post
update-alternatives --install %{_bindir}/mvn mvn %{homedir}/bin/mvn %{?maven_alternatives_priority}0 \
--slave %{_bindir}/mvnDebug mvnDebug %{homedir}/bin/mvnDebug \
--slave %{_mandir}/man1/mvn.1.gz mvn1 %{homedir}/bin/mvn.1.gz \
--slave %{_mandir}/man1/mvnDebug.1.gz mvnDebug1 %{homedir}/bin/mvn.1.gz \

%postun
if [ $1 -eq 0 ]; then
  update-alternatives --remove %{name} %{homedir}/bin/mvn
fi

%files -f .mfiles
%doc README.md
%license LICENSE NOTICE
%{homedir}
%config(noreplace) %{_sysconfdir}/m2%{?maven_version_suffix}.conf
%config(noreplace) %{confdir}/*
%ghost %{_bindir}/mvn*
%{_datadir}/bash-completion

%files help -f .mfiles-javadoc
%ghost %{_mandir}/man1/mvn*.gz

%changelog
* Fri Dec  6 2019 lingsheng <lingsheng@huawei.com> - 1:3.5.4-3
- Package init
