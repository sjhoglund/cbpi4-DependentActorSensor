# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.base import CBPiBase
from cbpi.api.sensor import CBPiSensor
from cbpi.api.dataclasses import NotificationAction, NotificationType

logger = logging.getLogger(__name__)

@parameters([Property.Actor(label="Base",  description="Select the actor you would like to add a dependency to."),
            Property.Sensor(label="SensorDependency", description="Select the sensor that the base actor will depend upon."),
            Property.Number(label="SensorValue", description="Input the sensor value needed to switch the 'Base Actor' ON."),
            Property.Select(label="notification", options=["Yes", "No"], description="Will show notifications in case of errors if set to yes")])

class DependentActorSensor(CBPiActor):

    def on_start(self):
        self.state = False
        self.base = self.props.get("Base", None)
        self.sensor_dependency = self.props.get("SensorDependency", None)
        self.sensor_min = int(self.props.get("SensorValue", 0))
        self.notification = self.props.get("notification", "Yes")
        self.init = False
        pass

    async def on(self, power=0):
        sensor_dep = self.cbpi.sensor.find_by_id(self.sensor_dependency)
        sensor_val = self.cbpi.sensor.get_sensor_value(self.sensor_dependency).get("value")
        
        if sensor_val >= self.sensor_min:
            await self.cbpi.actor.on(self.base)
#             self.state = True
#             if self.notification == "Yes":
#                 self.cbpi.notify("Powering of Actor tbd", "This pass %s" %(sensor_dep.name) ,NotificationType.INFO)
        else:
            await self.cbpi.actor.off(self.base)
            self.state = False
            if self.notification == "Yes":
                self.cbpi.notify("Powering of Actor prevented", "This is due to the current value of it's dependency %s" %(sensor_dep.name) ,NotificationType.ERROR)


    async def off(self):
        logger.info("ACTOR %s OFF " % self.base)
        await self.cbpi.actor.off(self.base)
        self.state = False

    def get_state(self):
        return self.state
    
    async def run(self):
        if self.init == False:
            if self.base is not None:
                await self.cbpi.actor.off(self.base)
                self.state = False
            self.init = True
        pass


def setup(cbpi):
    cbpi.plugin.register("Dependent Actor Sensor", DependentActorSensor)
    pass