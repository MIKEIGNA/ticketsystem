"""
Repair migration: the security_code column may or may not exist in production
depending on which partial migration steps ran previously.
This migration uses raw SQL with IF NOT EXISTS to safely add the column and
index only if they are missing, then fake-marks 0003 as applied.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0003_ticket_security_code"),
    ]

    operations = [
        migrations.RunSQL(
            # Forward: add column + index only if missing
            sql="""
                DO $$
                BEGIN
                    -- Add the column if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'bookings_ticket'
                          AND column_name = 'security_code'
                    ) THEN
                        ALTER TABLE bookings_ticket
                            ADD COLUMN security_code VARCHAR(19) NULL;
                    END IF;

                    -- Add the btree index if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE tablename = 'bookings_ticket'
                          AND indexname = 'bookings_ticket_security_code_85517eca'
                    ) THEN
                        CREATE INDEX bookings_ticket_security_code_85517eca
                            ON bookings_ticket (security_code);
                    END IF;

                    -- Add the like index if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE tablename = 'bookings_ticket'
                          AND indexname = 'bookings_ticket_security_code_85517eca_like'
                    ) THEN
                        CREATE INDEX bookings_ticket_security_code_85517eca_like
                            ON bookings_ticket (security_code varchar_pattern_ops);
                    END IF;

                    -- Add unique constraint if it doesn't exist
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE tablename = 'bookings_ticket'
                          AND indexname = 'bookings_ticket_security_code_key'
                    ) THEN
                        ALTER TABLE bookings_ticket
                            ADD CONSTRAINT bookings_ticket_security_code_key
                            UNIQUE (security_code);
                    END IF;
                END
                $$;
            """,
            # Reverse: no-op (don't drop on rollback)
            reverse_sql="SELECT 1;",
        ),
    ]
