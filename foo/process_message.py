""" Processing message actions """

from fantasm.action import FSMAction
import models

class IsMemeber(FSMAction):
    def execute(self, context, obj):
        context.logger.info('IsMemeber.execute()')
        context.logger.info("Process message key := %s" % (str(context['key'])))
        message = models.Message.get_by_id(context['key'].id())
        context['sender'] = message.sender
        account = models.Account.get_account_by_email(message.sender)

        if account:
            if account.is_expired:
                return 'expired'
            else:
                return 'member'
        else:
            return 'invite'

class InviteMemeber(FSMAction):
    def execute(self, context, obj):
        context.logger.info('InviteMemeber.execute()')
        context.logger.info("Queueing invitation to %s" % (context['sender']))

        #TODO: This we can push to the task queues for throttling.
        models.Invitation.send_invitation(context['sender'])
        pass

class ExpiredMemeber(FSMAction):
    def execute(self, context, obj):
        #TODO: lets send users that are expired a message.
        return 'blacklist' #or pass

class BlacklistMemeber(FSMAction):
    def execute(self, context, obj):
        context.logger.info('BlacklistMemeber.execute()')
        message = models.Message.get_by_id(context['key'].id())
        models.BlackList.blacklist_email(message.sender)
        pass

class IdentifySubjectType(FSMAction):
    def execute(self, context, obj):
       return 'tags' #or topic

class ProcessTags(FSMAction):
    def execute(self, context, obj):
       return 'complete'

class ProcessTopic(FSMAction):
    def execute(self, context, obj):
       return 'complete'

class ProcessContent(FSMAction):
    def execute(self, context, obj):
        pass