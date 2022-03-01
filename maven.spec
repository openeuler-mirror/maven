%bcond_without  logback
%global bundled_slf4j_version 1.7.25
%global homedir %{_datadir}/%{name}%{?maven_version_suffix}
%global confdir %{_sysconfdir}/%{name}%{?maven_version_suffix}
Name:                maven
Epoch:               1
Version:             3.6.3
Release:             1
Summary:             Java project management and project comprehension tool
License:             ASL 2.0 and MIT
URL:                 http://maven.apache.org/
Source0:             http://archive.apache.org/dist/maven/maven-3/%{version}/source/apache-maven-%{version}-src.tar.gz
Source1:             maven-bash-completion
Source2:             mvn.1
Patch1:              0001-adapt-mvn-script.patch
Patch2:              0002-invoke-logback-via-reflection.patch
Patch3:              0003-use-non-shaded-HTTP-wagon.patch
Patch4:              0004-remove-dependency-on-powermock.patch

BuildRequires:       maven-local
BuildRequires:       mvn(com.google.inject:guice::no_aop:) mvn(commons-cli:commons-cli)
BuildRequires:       mvn(commons-jxpath:commons-jxpath) mvn(javax.annotation:jsr250-api)
BuildRequires:       mvn(javax.inject:javax.inject) mvn(junit:junit)
BuildRequires:       mvn(org.apache.commons:commons-lang3) mvn(org.apache.maven:maven-parent:pom:)
BuildRequires:       mvn(org.apache.maven.plugins:maven-assembly-plugin)
BuildRequires:       mvn(org.apache.maven.plugins:maven-dependency-plugin)
BuildRequires:       mvn(org.apache.maven.plugins:maven-failsafe-plugin)
BuildRequires:       mvn(org.apache.maven.resolver:maven-resolver-api)
BuildRequires:       mvn(org.apache.maven.resolver:maven-resolver-connector-basic)
BuildRequires:       mvn(org.apache.maven.resolver:maven-resolver-impl)
BuildRequires:       mvn(org.apache.maven.resolver:maven-resolver-spi)
BuildRequires:       mvn(org.apache.maven.resolver:maven-resolver-transport-wagon)
BuildRequires:       mvn(org.apache.maven.resolver:maven-resolver-util)
BuildRequires:       mvn(org.apache.maven.shared:maven-shared-utils)
BuildRequires:       mvn(org.apache.maven.wagon:wagon-file)
BuildRequires:       mvn(org.apache.maven.wagon:wagon-http)
BuildRequires:       mvn(org.apache.maven.wagon:wagon-provider-api)
BuildRequires:       mvn(org.codehaus.modello:modello-maven-plugin) >= 1.11
BuildRequires:       mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires:       mvn(org.codehaus.plexus:plexus-classworlds)
BuildRequires:       mvn(org.codehaus.plexus:plexus-component-annotations)
BuildRequires:       mvn(org.codehaus.plexus:plexus-component-metadata)
BuildRequires:       mvn(org.codehaus.plexus:plexus-interpolation)
BuildRequires:       mvn(org.codehaus.plexus:plexus-utils) >= 3.2.0
BuildRequires:       mvn(org.eclipse.sisu:org.eclipse.sisu.inject)
BuildRequires:       mvn(org.eclipse.sisu:org.eclipse.sisu.plexus)
BuildRequires:       mvn(org.eclipse.sisu:sisu-maven-plugin) mvn(org.fusesource.jansi:jansi)
BuildRequires:       mvn(org.hamcrest:hamcrest-library)
BuildRequires:       mvn(org.jsoup:jsoup)
BuildRequires:       mvn(org.mockito:mockito-core) >= 2 mvn(org.slf4j:jcl-over-slf4j)
BuildRequires:       mvn(org.slf4j:slf4j-api) mvn(org.slf4j:slf4j-simple)
BuildRequires:       mvn(org.sonatype.plexus:plexus-cipher)
BuildRequires:       mvn(org.sonatype.plexus:plexus-sec-dispatcher) mvn(org.xmlunit:xmlunit-core) mvn(org.xmlunit:xmlunit-matchers)
BuildRequires:       slf4j-sources = %{bundled_slf4j_version}
%if %{with logback}
BuildRequires:       mvn(ch.qos.logback:logback-classic)
%endif
Requires:            %{name}-lib = %{epoch}:%{version}-%{release}
Requires(post):      /usr/sbin/update-alternatives
Requires(postun):    /usr/sbin/update-alternatives
Requires:            java-1.8.0-devel
Requires:            aopalliance apache-commons-cli apache-commons-codec apache-commons-io
Requires:            apache-commons-lang3 apache-commons-logging atinject cdi-api
Requires:            geronimo-annotation google-guice guava20 hawtjni-runtime httpcomponents-client
Requires:            httpcomponents-core jansi jansi-native jcl-over-slf4j maven-resolver-api
Requires:            maven-resolver-connector-basic maven-resolver-impl maven-resolver-spi
Requires:            maven-resolver-transport-wagon maven-resolver-util maven-shared-utils
Requires:            maven-wagon-file maven-wagon-http maven-wagon-http-shared
Requires:            maven-wagon-provider-api plexus-cipher plexus-classworlds
Requires:            plexus-containers-component-annotations plexus-interpolation
Requires:            plexus-sec-dispatcher plexus-utils sisu-inject sisu-plexus slf4j
BuildArch:           noarch

%description
Maven is a software project management and comprehension tool. Based on the
concept of a project object model (POM), Maven can manage a project's build,
reporting and documentation from a central piece of information.

%package        lib
Summary:             Core part of Maven
OrderWithRequires:   xmvn-minimal
Requires:            javapackages-tools
Provides:            bundled(slf4j) = %{bundled_slf4j_version}

%description    lib
Core part of Apache Maven that can be used as a library.

%package        javadoc
Summary:             API documentation for %{name}

%description    javadoc
%{summary}.

%prep
%setup -q -n apache-%{name}-%{version}
%patch1 -p1
%patch3 -p1
%patch4 -p1
find -name '*.jar' -not -path '*/test/*' -delete
find -name '*.class' -delete
find -name '*.bat' -delete
%pom_remove_dep -r :powermock-reflect
sed -i 's:\r::' apache-maven/src/conf/settings.xml
rm apache-maven/src/main/appended-resources/META-INF/LICENSE.vm
%pom_remove_plugin -r :animal-sniffer-maven-plugin
%pom_remove_plugin -r :apache-rat-plugin
%pom_remove_plugin -r :maven-site-plugin
%pom_remove_plugin -r :buildnumber-maven-plugin
sed -i "
/buildNumber=/ {
  s/=.*/=openEuler %{version}-%{release}/
  s/%{dist}$//
}
/timestamp=/ d
" `find -name build.properties`
%mvn_package :apache-maven __noinstall
%if %{without logback}
%pom_remove_dep -r :logback-classic
%patch2 -p1
%endif
%mvn_alias :maven-resolver-provider :maven-aether-provider

%pom_xpath_inject 'pom:build/pom:plugins' '
<plugin>
    <groupId>org.eclipse.sisu</groupId>
    <artifactId>sisu-maven-plugin</artifactId>
</plugin>' maven-model-builder/pom.xml

%pom_xpath_set "//pom:dependency[pom:artifactId='jansi']/pom:version" 1.18

%build
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8
mkdir m2home
(cd m2home
    tar --delay-directory-restore -xvf ../apache-maven/target/*tar.gz
)

%install
%mvn_install
export M2_HOME=$(pwd)/m2home/apache-maven-%{version}%{?ver_add}
install -d -m 755 %{buildroot}%{homedir}/conf
install -d -m 755 %{buildroot}%{confdir}
install -d -m 755 %{buildroot}%{_datadir}/bash-completion/completions/
cp -a $M2_HOME/{bin,lib,boot} %{buildroot}%{homedir}/
xmvn-subst -R %{buildroot} -s %{buildroot}%{homedir}
build-jar-repository -s -p %{buildroot}%{homedir}/lib \
    httpcomponents/{httpclient,httpcore} maven-wagon/http-shared
rm %{buildroot}%{homedir}/lib/jboss-interceptors*.jar
rm %{buildroot}%{homedir}/lib/javax.el-api*.jar
ln -s %{_jnidir}/jansi-native/jansi-linux.jar %{buildroot}%{homedir}/lib/
install -p -m 644 %{SOURCE2} %{buildroot}%{homedir}/bin/
gzip -9 %{buildroot}%{homedir}/bin/mvn.1
install -p -m 644 %{SOURCE1} %{buildroot}%{_datadir}/bash-completion/completions/mvn%{?maven_version_suffix}
mv $M2_HOME/bin/m2.conf %{buildroot}%{_sysconfdir}/m2%{?maven_version_suffix}.conf
ln -sf %{_sysconfdir}/m2%{?maven_version_suffix}.conf %{buildroot}%{homedir}/bin/m2.conf
mv $M2_HOME/conf/settings.xml %{buildroot}%{confdir}/
ln -sf %{confdir}/settings.xml %{buildroot}%{homedir}/conf/settings.xml
mv $M2_HOME/conf/logging %{buildroot}%{confdir}/
ln -sf %{confdir}/logging %{buildroot}%{homedir}/conf
install -d -m 755 %{buildroot}%{_bindir}/
install -d -m 755 %{buildroot}%{_mandir}/man1/
touch %{buildroot}%{_bindir}/{mvn,mvnDebug}
touch %{buildroot}%{_mandir}/man1/{mvn,mvnDebug}.1

%post
update-alternatives --install %{_bindir}/mvn mvn %{homedir}/bin/mvn %{?maven_alternatives_priority}0 \
--slave %{_bindir}/mvnDebug mvnDebug %{homedir}/bin/mvnDebug \
--slave %{_mandir}/man1/mvn.1.gz mvn1 %{homedir}/bin/mvn.1.gz \
--slave %{_mandir}/man1/mvnDebug.1.gz mvnDebug1 %{homedir}/bin/mvn.1.gz \

%postun
if [[ $1 -eq 0 ]]; then update-alternatives --remove mvn %{homedir}/bin/mvn; fi

%files lib -f .mfiles
%doc README.md
%license LICENSE NOTICE
%{homedir}
%dir %{confdir}
%dir %{confdir}/logging
%config(noreplace) %{_sysconfdir}/m2%{?maven_version_suffix}.conf
%config(noreplace) %{confdir}/settings.xml
%config(noreplace) %{confdir}/logging/simplelogger.properties

%files
%ghost %{_bindir}/mvn
%ghost %{_bindir}/mvnDebug
%{_datadir}/bash-completion
%ghost %{_mandir}/man1/mvn.1.gz
%ghost %{_mandir}/man1/mvnDebug.1.gz

%files javadoc -f .mfiles-javadoc
%license LICENSE NOTICE

%changelog
* Mon Feb 21 2022 Ge Wang <wangge20@huawei.com> - 1:3.6.3-1
- upgrade to version 3.6.3

* Sat Jul 24 2021 wangyue <wangyue92@huawei.com> - 1:3.5.4-10
- fix maven downgrade error

* Fri Jul 16 2021 wutao <wutao61@huawei.com> - 1:3.5.4-9
- fix CVE-2021-26291

* Thu Oct 15 2020 lingsheng <lingsheng@huawei.com> - 1:3.5.4-8
- Change require to java-1.8.0-devel

* Sat Sep 12 2020 yaokai13 <yaokai13@huawei.com> - 1:3.5.4-7
- Fix the spelling mistakes

* Thu Sep 3 2020 leiju <leiju4@huawei.com> - 1:3.5.4-6
- Fix the build error

* Fri Mar 06 2020 lihao <lihao129@huawei.com> - 1:3.5.4-5
- Fix incorrect maven home path

* Fri Mar 06 2020 lihao <lihao129@huawei.com> - 1:3.5.4-4
- Use Mockito 1.x instead of 2.x

* Fri Dec  6 2019 lingsheng <lingsheng@huawei.com> - 1:3.5.4-3
- Package init
