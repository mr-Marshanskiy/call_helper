import datetime
import pdb

from crum import get_current_user
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from breaks.models.breaks import Break
from breaks.models.replacements import Replacement, ReplacementMember
from breaks.serializers.nested.replacements import ReplacementShortSerializer
from common.serializers.mixins import InfoModelSerializer, DictMixinSerializer, \
    ExtendedModelSerializer
from common.validationrs import Time15MinutesValidator

User = get_user_model()


class BreakMeRetrieveSerializer(InfoModelSerializer):
    status = DictMixinSerializer()
    replacement = ReplacementShortSerializer()

    class Meta:
        model = Break
        fields = (
            'id',
            'replacement',
            'break_start',
            'break_end',
            'status',
        )


class BreakMeUpdateSerializer(InfoModelSerializer):

    class Meta:
        model = Break
        fields = (
            'id',
            'break_start',
            'break_end',
        )
        extra_kwargs = {
            'break_start': {'validators': [Time15MinutesValidator()]},
            'break_end': {'validators': [Time15MinutesValidator()]},
        }

    def validate(self, attrs):
        try:
            instance_id = self.instance.pk
        except:
            instance_id = None

        replacement = self.get_object_from_url(Replacement)
        user = get_current_user()

        member = ReplacementMember.objects.filter(
            replacement=replacement,
            member__employee__user=user
        ).first()

        now = timezone.now().date()
        if replacement.date != now:
            raise ParseError(
                'Время резервирования перерыва уже закончилось или ещё не началось.'
            )
        if not member:
            raise ParseError('У вас нет доступа к текущей смене.')

        if attrs['break_start'] < replacement.break_start:
            raise ParseError(
                'Время начала не должно быть меньше времени, указанного в смене.'
            )
        if attrs['break_end'] > replacement.break_end:
            raise ParseError(
                'Время окончания не должно быть больше времени, указанного в смене.'
            )
        if attrs['break_start'] >= attrs['break_end']:
            raise ParseError(
                'Время начала не должно быть больше времени окончания.'
            )

        max_duration = datetime.timedelta(minutes=replacement.break_max_duration)
        break_start = datetime.datetime.combine(datetime.date.today(), attrs['break_start'])
        break_end = datetime.datetime.combine(datetime.date.today(), attrs['break_end'])
        if break_start + max_duration < break_end:
            raise ParseError(
                'Продолжительность обеда превышает максимальное установленное значение.'
            )

        free_breaks = replacement.free_breaks_available(
            attrs['break_start'], attrs['break_end'], instance_id
        )
        if free_breaks <= replacement.min_active:
            raise ParseError('Нет свободных мест на выбранный интервал.')
        attrs['replacement'] = replacement
        attrs['member'] = member

        if not instance_id:
            if replacement.breaks.filter(member=member).exists():
                raise ParseError(
                    'Вы уже зарезервировали обеденный перерыв.'
                )

        return attrs


class BreakScheduleSerializer(serializers.Serializer):
    final_line = serializers.SerializerMethodField()

    def get_final_line(self, instance):
        line = [self.get_instance(instance)]
        pre_blank = self.get_pre_blank(instance)
        if pre_blank['colspan'] > 0:
            line.append(pre_blank)
        line.append(self.get_break(instance))
        post_blank = self.get_post_blank(instance)
        if post_blank['colspan'] > 0:
            line.append(post_blank)
        return line

    def get_instance(self, instance):
        result = self._convert_to_cell(
            value=instance.member.member.employee.user.full_name,
            color='#fff',
            span=2,
        )
        return result

    def get_pre_blank(self, instance):
        span = self._get_span_count(
            instance.replacement.break_start, instance.break_start
        )
        return self._convert_to_cell(span=span)

    def get_break(self, instance):
        span = self._get_span_count(instance.break_start, instance.break_end)
        break_start = instance.break_start.strftime('%H:%M')
        break_end = instance.break_start.strftime('%H:%M')
        value = f'{break_start} - {break_end}'
        color = instance.status.color
        return self._convert_to_cell(value, color, span)

    def get_post_blank(self, instance):
        span = self._get_span_count(
           instance.break_end, instance.replacement.break_end
        )
        return self._convert_to_cell(span=span)

    def _convert_to_cell(self, value='', color='#fff', span=None):
        obj = {'value': value, 'color': color}
        if span is not None:
            obj['colspan'] = span
        return obj

    def _get_span_count(self, start_board, start_instance):
        board_minutes = start_board.hour * 60 + start_board.minute
        instance_minutes = start_instance.hour * 60 + start_instance.minute
        span = int((instance_minutes - board_minutes) / 15)
        return span

    def to_representation(self, instance):
        return self.fields['final_line'].to_representation(instance)

