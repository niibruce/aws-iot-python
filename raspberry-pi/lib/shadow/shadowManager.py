'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''


class _shadowAction:
    _shadowName = None
    _actionName = None
    _topicGeneral = None
    _topicAccept = None
    _topicReject = None
    _topicDelta = None
    isDelta = False
    _actionType = ["get", "update", "delete", "delta"]

    def __init__(self, srcShadowName, srcActionName):
        if srcActionName is None or srcActionName not in self._actionType:
            raise TypeError("Unsupported shadow action.")
        self._shadowName = srcShadowName
        self._actionName = srcActionName
        self.isDelta = srcActionName == "delta"
        if self.isDelta:
            self._topicDelta = "$aws/things/" + str(self._shadowName) + "/shadow/update/delta"
        else:
            self._topicGeneral = "$aws/things/" + str(self._shadowName) + "/shadow/" + str(self._actionName)
            self._topicAccept = "$aws/things/" + str(self._shadowName) + "/shadow/" + str(self._actionName) + "/accepted"
            self._topicReject = "$aws/things/" + str(self._shadowName) + "/shadow/" + str(self._actionName) + "/rejected"

    def getTopicGeneral(self):
        return self._topicGeneral

    def getTopicAccept(self):
        return self._topicAccept

    def getTopicReject(self):
        return self._topicReject

    def getTopicDelta(self):
        return self._topicDelta


class shadowManager:
    # Tool handler
    _mqttCoreHandler = None
    # Tool data structure

    def __init__(self, srcMQTTCore):
        # Load in mqttCore
        if srcMQTTCore is None:
            raise TypeError("None type inputs detected.")
        self._mqttCoreHandler = srcMQTTCore

    def getClientID(self):
        return self._mqttCoreHandler.getClientID()

    def basicShadowPublish(self, srcShadowName, srcShadowAction, srcPayload):
        currentShadowAction = _shadowAction(srcShadowName, srcShadowAction)
        self._mqttCoreHandler.publish(currentShadowAction.getTopicGeneral(), srcPayload, 0, False)

    def basicShadowSubscribe(self, srcShadowName, srcShadowAction, srcCallback):
        currentShadowAction = _shadowAction(srcShadowName, srcShadowAction)
        if currentShadowAction.isDelta:
            self._mqttCoreHandler.subscribe(currentShadowAction.getTopicDelta(), 0, srcCallback)
        else:
            self._mqttCoreHandler.subscribe(currentShadowAction.getTopicAccept(), 0, srcCallback)
            self._mqttCoreHandler.subscribe(currentShadowAction.getTopicReject(), 0, srcCallback)

    def basicShadowUnsubscribe(self, srcShadowName, srcShadowAction):
        currentShadowAction = _shadowAction(srcShadowName, srcShadowAction)
        if currentShadowAction.isDelta:
            self._mqttCoreHandler.unsubscribe(currentShadowAction.getTopicDelta())
        else:
            self._mqttCoreHandler.unsubscribe(currentShadowAction.getTopicAccept())
            self._mqttCoreHandler.unsubscribe(currentShadowAction.getTopicReject())
