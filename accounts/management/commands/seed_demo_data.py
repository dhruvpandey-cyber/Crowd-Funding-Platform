from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from campaigns.models import Campaign, Category, RewardTier
from moderation.models import Report
from notifications_app.models import Notification
from payments.models import Payment
from pledges.models import Pledge


class Command(BaseCommand):
    help = "Seed demo users, campaigns, rewards, pledges, and reports"

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin_demo",
            defaults={"email": "admin@crowdspark.dev", "role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        admin.set_password("Admin@12345")
        admin.save()

        creator, _ = User.objects.get_or_create(
            username="creator_demo",
            defaults={
                "email": "creator@crowdspark.dev",
                "role": User.Role.CREATOR,
                "is_creator_verified": True,
                "first_name": "Asha",
                "last_name": "Sharma",
            },
        )
        creator.set_password("Creator@12345")
        creator.save()

        backer, _ = User.objects.get_or_create(
            username="backer_demo",
            defaults={
                "email": "backer@crowdspark.dev",
                "role": User.Role.BACKER,
                "first_name": "Rohan",
                "last_name": "Verma",
            },
        )
        backer.set_password("Backer@12345")
        backer.save()

        tech, _ = Category.objects.get_or_create(name="Technology", defaults={"description": "Innovative tech projects"})
        edu, _ = Category.objects.get_or_create(name="Education", defaults={"description": "Learning initiatives"})

        campaign_1, _ = Campaign.objects.get_or_create(
            title="Solar Study Lamp for Rural Students",
            creator=creator,
            defaults={
                "category": edu,
                "short_description": "Affordable solar lamps for low-light study areas.",
                "story": "We are building durable, low-cost lamps and distributing them to schools.",
                "goal_amount": Decimal("50000.00"),
                "min_pledge_amount": Decimal("200.00"),
                "deadline": timezone.now() + timedelta(days=25),
                "status": Campaign.Status.ACTIVE,
            },
        )

        campaign_2, _ = Campaign.objects.get_or_create(
            title="Smart IoT Soil Monitor",
            creator=creator,
            defaults={
                "category": tech,
                "short_description": "A low-cost farm sensor kit for small farmers.",
                "story": "This project creates open hardware devices for precision irrigation.",
                "goal_amount": Decimal("75000.00"),
                "min_pledge_amount": Decimal("500.00"),
                "deadline": timezone.now() + timedelta(days=30),
                "status": Campaign.Status.ACTIVE,
            },
        )

        RewardTier.objects.get_or_create(
            campaign=campaign_1,
            title="Supporter",
            defaults={"description": "Thank you email and donor wall mention", "amount": Decimal("200.00")},
        )
        RewardTier.objects.get_or_create(
            campaign=campaign_1,
            title="Impact Kit",
            defaults={"description": "Sponsor one full lamp kit", "amount": Decimal("1500.00")},
        )
        reward_iot, _ = RewardTier.objects.get_or_create(
            campaign=campaign_2,
            title="Early Kit",
            defaults={"description": "Get an early sensor kit", "amount": Decimal("2500.00")},
        )

        pledge, created = Pledge.objects.get_or_create(
            backer=backer,
            campaign=campaign_2,
            amount=Decimal("2500.00"),
            defaults={"reward_tier": reward_iot, "status": Pledge.Status.CAPTURED},
        )
        if created:
            Payment.objects.create(
                pledge=pledge,
                gateway="sandbox",
                transaction_id=f"SEED-TXN-{pledge.id:04d}",
                amount=pledge.amount,
                status=Payment.Status.SUCCESS,
                paid_at=timezone.now(),
            )

        Report.objects.get_or_create(
            reporter=backer,
            campaign=campaign_1,
            reason="Need clearer timeline",
            defaults={"details": "Please share delivery milestones", "status": Report.Status.OPEN},
        )

        Notification.objects.get_or_create(
            user=creator,
            title="Demo data seeded",
            defaults={"message": "Your demo campaigns are ready for presentation."},
        )
        Notification.objects.get_or_create(
            user=backer,
            title="Thanks for supporting",
            defaults={"message": "You have one demo pledge in your dashboard."},
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(self.style.WARNING("Demo credentials:"))
        self.stdout.write("admin_demo / Admin@12345")
        self.stdout.write("creator_demo / Creator@12345")
        self.stdout.write("backer_demo / Backer@12345")
