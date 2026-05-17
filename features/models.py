<<<<<<< HEAD


# Create your models here.
from django.db import models


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question
=======
from django.db import models

# Create your models here.
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
