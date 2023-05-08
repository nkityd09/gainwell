========================================
Community MySQL Collection Release Notes
========================================

.. contents:: Topics

This changelog describes changes after version 2.0.0.

v3.1.0
======

Release Summary
---------------

This is the minor release of the ``community.mysql`` collection.
This changelog contains all changes to the modules in this collection
that have been added after the release of ``community.mysql`` 3.0.0.

Minor Changes
-------------

- Added explicit description of the supported versions of databases and connectors. Changes to the collection are **NOT** tested against database versions older than `mysql 5.7.31` and `mariadb 10.2.37` or connector versions older than `pymysql 0.7.10` and `mysqlclient 2.0.1`. (https://github.com/ansible-collections/community.mysql/discussions/141)
- mysql_user - added the ``force_context`` boolean option to set the default database context for the queries to be the ``mysql`` database. This way replication/binlog filters can catch the statements (https://github.com/ansible-collections/community.mysql/issues/265).

Bugfixes
--------

- Collection core functions - use vendored version of ``distutils.version`` instead of the deprecated Python standard library ``distutils`` (https://github.com/ansible-collections/community.mysql/pull/269).

v3.0.0
======

Release Summary
---------------

This is the major release of the ``community.mysql`` collection.
This changelog contains all breaking changes to the modules in this collection
that have been added after the release of ``community.mysql`` 2.3.2.

Breaking Changes / Porting Guide
--------------------------------

- mysql_replication - remove ``Is_Slave`` and ``Is_Master`` return values (were replaced with ``Is_Primary`` and ``Is_Replica`` (https://github.com/ansible-collections    /community.mysql/issues/145).
- mysql_replication - remove the mode options values containing ``master``/``slave`` and the master_use_gtid option ``slave_pos`` (were replaced with corresponding ``primary``/``replica`` values) (https://github.com/ansible-collections/community.mysql/issues/145).
- mysql_user - remove support for the `REQUIRESSL` special privilege as it has ben superseded by the `tls_requires` option (https://github.com/ansible-collections/community.mysql/discussions/121).
- mysql_user - validate privileges using database engine directly (https://github.com/ansible-collections/community.mysql/issues/234 https://github.com/ansible-collections/community.mysql/pull/243). Do not validate privileges in this module anymore.
