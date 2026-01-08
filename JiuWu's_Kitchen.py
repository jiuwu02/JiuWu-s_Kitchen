# coding: UTF-8
import math
import random
import json
import re

import pyspigot as ps  # type: ignore

from org.bukkit import Location, Bukkit, Material, Sound, Registry, Particle, NamespacedKey  # type: ignore
from org.bukkit.util import Transformation  # type: ignore
from org.bukkit.block import BlockFace  # type: ignore
from org.bukkit.entity import Player, EntityType, ItemDisplay  # type: ignore
from org.bukkit.inventory import EquipmentSlot, ItemStack  # type: ignore
from org.bukkit.event.player import PlayerInteractEvent  # type: ignore
from org.bukkit.event.block import BlockBreakEvent, Action  # type: ignore
from org.bukkit.event.inventory import InventoryType, InventoryCloseEvent  # type: ignore

from java.lang import System  # type: ignore
from java.time import Duration  # type: ignore
from org.joml import Vector3f, Quaternionf  # type: ignore

from net.kyori.adventure.text import Component, TextReplacementConfig # type: ignore
from net.kyori.adventure.text.serializer.gson import GsonComponentSerializer # type: ignore
from net.kyori.adventure.text.serializer.plain import PlainTextComponentSerializer # type: ignore
from net.kyori.adventure.text.serializer.legacy import LegacyComponentSerializer # type: ignore
from net.kyori.adventure.text.minimessage import MiniMessage # type: ignore
from net.kyori.adventure.title import Title # type: ignore

class ConfigManager:
    """配置文件管理类"""

    config = None
    choppingBoardRecipe = None
    wokRecipe = None
    grinderRecipe = None
    steamerRecipe = None
    data = None
    prefix = None

    @staticmethod
    def setConfigValue(configFile, path, defaultValue, comments=None):
        """为配置项设置默认值和注释

        参数
            configFile: 配置文件对象
            path: 配置项路径
            defaultValue: 默认值
            comments: 注释列表(可选)
        """
        if not configFile.contains(path):
            configFile.setIfNotExists(path, defaultValue)
            if comments is not None:
                configFile.setComments(path, comments)

    @staticmethod
    def loadConfig():
        """加载并初始化插件配置文件

        返回
            配置对象
        """
        configPath = "JiuWu's Kitchen/Config.yml"
        configFile = ps.config.loadConfig(configPath)

        # 通用配置
        ConfigManager.setConfigValue(configFile, "Setting.General.SearchRadius", 0.45,[u"搜索展示实体的半径"])

        # 砧板设置
        ConfigManager.setConfigValue(configFile,"Setting.ChoppingBoard.Drop",True,[u"砧板处理完成后是否掉落成品"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.StealthInteraction", True, [
            u"是否需要在潜行状态下与砧板交互",
            u"启用时: 玩家必须潜行才能使用砧板功能",
            u"禁用时: 玩家可直接交互无需潜行"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Custom", False, [
            u"是否使用自定义方块作为砧板",
            u"启用时: 使用兼容插件的方块 (例如: CraftEngine)",
            u"禁用时: 使用原版的方块",
            "",
            u"CraftEngine的方块: craftengine <Key>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Material", "OAK_LOG")
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.SpaceRestriction", False, [
            u"砧板上方是否允许存在方块",
            u"启用时: 砧板上方有方块时无法使用",
            u"禁用时: 砧板上方允许存在方块"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Delay", 1.0, [
            u"砧板交互的最小间隔时间 (秒)",
            u"防止玩家连续快速交互",
            u"设置为0表示无延迟"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.KitchenKnife.Custom", False, [
            u"是否使用自定义刀具",
            u"启用时: 使用兼容插件的物品 (例如: CraftEngine, MMOItems)",
            u"禁用时: 使用原版物品",
            "",
            u"CraftEngine物品: craftengine <Key>:<ID>",
            u"MMOItems物品: mmoitems <Type>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Enable", True, [
            u"是否启用砧板事件",
            u"启用时: 切菜时有概率切伤手指"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Chance", 10)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Value", 2)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.KitchenKnife.Material", ["minecraft IRON_AXE"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Offset.Y", 1.02)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Rotation.X", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Rotation.Y", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Rotation.Z", 0.0, [
            u"允许Z轴旋转角度为小数 (0.0, 360.0)",
            u"也允许为一个范围值随机数 (0.0-360.0)"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Scale", 0.5)

        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Offset.Y", 1.125)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Rotation.X", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Rotation.Y", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Rotation.Z", 0.0, [
            u"允许Z轴旋转角度为小数 (0.0, 360.0)",
            u"也允许为一个范围值随机数 (0.0-360.0)"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Scale", 0.25)

        # 炒锅设置
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Drop", True, [u"炒锅烹饪完成后是否掉落成品"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.StealthInteraction", True, [
            u"控制与炒锅交互是否需要潜行",
            "",
            u"启用时: 所有炒锅交互 (放入食材/取出食材/翻炒) 都需要潜行状态",
            u"如果未启用 Setting.Wok.NeedBowl 选项，则空手盛取成品 \"不需要\" 潜行状态",
            "",
            u"禁用时: 所有炒锅交互 (放入食材/取出食材/翻炒) 都不需要潜行状态",
            u"如果未启用 Setting.Wok.NeedBowl 选项，则空手盛取成品 \"需要\" 潜行状态"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Custom", False, [
            u"是否使用自定义炒锅方块",
            u"启用时: 使用兼容插件的方块(例如: CraftEngine)",
            u"禁用时: 使用原版方块",
            "",
            u"CraftEngine的方块: craftengine <Key>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Material", "IRON_BLOCK")
        ConfigManager.setConfigValue(
            configFile, "Setting.Wok.HeatControl", {"CAMPFIRE": 1,"MAGMA_BLOCK": 2,"LAVA": 3,},[
                u"定义不同热源的烹饪强度",
                u"数值越高代表火候越猛",
                "",
                u"支持 CraftEngine 插件的方块/家具",
                u"CraftEngine的方块: craftengine <Key>:<ID>: <火候大小>"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.NeedBowl", True, [
            u"控制从炒锅盛出成品是否需要碗",
            u"启用时: 必须手持碗才能盛出成品",
            u"禁用时: 空手即可直接盛出成品",
            u"注意: 如果启用则盛出操作是否要求潜行由 Setting.Wok.StealthInteraction 控制"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.InvalidRecipeOutput", "STONE", [
            u"该选项用于当玩家放入不完整或无效的食材组合时",
            u"将成品盛出后会得到这个物品作为失败产物"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Delay", 5, [
            u"炒锅翻炒食材的延迟时间 (秒)",
            u"这个值应该小于 Setting.Wok.TimeOut"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Damage.Enable", True, [
            u"是否启用炒锅取出食材烫伤事件",
            u"启用时: 如果锅内存在食材并且已经翻炒过，这时候取出食材将会受到伤害",
            u"禁用时: 从炒锅取出食材时将不会受到任何伤害"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Damage.Value", 2)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Failure.Enable", True, [
            u"是否启用炒锅烹饪失败事件",
            u"启用时: 即使食材和步骤都正确，也有概率烹饪失败",
            u"禁用时: 只要食材和步骤正确，烹饪必定成功"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Failure.Chance", 5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Failure.Type", "BONE_MEAL", [
            u"炒锅烹饪失败时生成的产物类型"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.TimeOut", 30, [
            u"单次翻炒操作后的最大等待时间 (秒)",
            u"每次翻炒操作后会重置此计时器",
            u"计时结束前未再次翻炒: 锅内食材会烧焦变为失败产物"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Spatula.Custom", False, [
            u"是否使用自定义炒菜铲",
            u"启用时: 使用兼容插件的物品 (例如: CraftEngine, MMOItems)",
            u"禁用时: 使用原版物品",
            u"CraftEngine物品: craftengine <Key>:<ID>",
            u"MMOItems物品: mmoitems <Type>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Spatula.Material", ["minecraft IRON_SHOVEL"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Offset.Y", 1.02)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Rotation.X", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Rotation.Y", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Rotation.Z", "0.0-90.0", [
            u"允许Z轴旋转角度为小数 (0.0, 360.0)",
            u"也允许为一个范围值随机数 (0.0-360.0)"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Scale", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Offset.Y", 1.125)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Rotation.X", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Rotation.Y", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Rotation.Z", 0.0, [
            u"允许Z轴旋转角度为小数 (0.0, 360.0)",
            u"也允许为一个范围值随机数 (0.0-360.0)",
            u"",
            u"暂不推荐使用"
            ])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Scale", 0.25)

        # 研磨机设置
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.Drop", True, [u"研磨机研磨完成后是否掉落成品"])
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.StealthInteraction", True, [
            u"与研磨机交互是否需要潜行"])
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.Custom", False, [
            u"是否使用自定义研磨机方块",
            u"启用时: 使用兼容插件的方块(例如: CraftEngine)",
            u"禁用时: 使用原版方块",
            "",
            u"CraftEngine的方块: craftengine <Key>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.Material", "GRINDSTONE")
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.CheckDelay", 20, [
            u"研磨机检查完成状态的延迟时间 (Tick)",
            u"这个值也决定了研磨时播放粒子效果与声音播放的间隔"
        ])

        # 蒸锅设置
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Material", "BARREL", [
            u"CraftEngine的方块: craftengine <Key>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.StealthInteraction", True, [
            u"是否需要在潜行状态下与蒸锅交互",
            u"启用时: 玩家必须潜行才能使用砧板功能",
            u"禁用时: 玩家可直接交互无需潜行"])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.OpenInventory.Type", "HOPPER", [
            u"打开的容器类型",
            u"详细请参考: https://jd.papermc.io/paper/1.21.11/org/bukkit/event/inventory/InventoryType.html"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.OpenInventory.Title", u"<dark_gray>蒸锅")
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.OpenInventory.Solt", 9, [
            u"当 Setting.Steamer.OpenInventory.Type 为 CHEST 时才有效"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.HeatControl", ["FURNACE", "SMOKER"], [
            u"能给蒸锅提供热源的方块",
            u"",
            u"CraftEngine的方块: craftengine <Key>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Ignite", True, [
            u"如果热源方块可以被点燃那么添加燃料后是否将热源方块点燃"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Fuel", {
            "STICK": 5,
            "COAL": 80,
            "CHARCOAL": 80,
        }, [
            u"允许向蒸锅添加的燃料，单位秒",
            u""
            u"CraftEngine物品: craftengine <Key>:<ID>",
            u"MMOItems物品: mmoitems <Type>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Moisture", [
            "WATER_BUCKET & BUCKET & 120",
            "POTION & GLASS_BOTTLE & 40"
        ], [
            u"物品能为蒸锅提供的水份",
            u"输入物 & 输出物 & 提供的水分值",
            u"如果不想拥有输出物，则将输出物写为 AIR",
            u"",
            u"CraftEngine物品: craftengine <Key>:<ID>",
            u"MMOItems物品: mmoitems <Type>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.ResetToZero", True, [
            u"如果设置为 True，那么当蒸锅蒸汽为 0 的时候，所有在蒸锅内的烹饪进度都将重置为 0",
            u"如果设置为 False，那么将继续保留当前烹饪进度"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.SteamProductionEfficiency", 10, [
            u"蒸汽产出效率，这个选项控制了物品给蒸锅提供的水份每秒可以将 1 水份转换为 10 蒸汽",
            u"即 10蒸汽/s"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.SteamConversionEfficiency", 1, [
            u"蒸汽转换效率，这个选项控制了食材使用蒸汽的速率",
            u"即 1蒸汽/s"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.SteamConsumptionEfficiency", 1, [
            u"蒸汽消耗效率，这个选项控制了蒸锅默认消耗的蒸汽速率，即使没有食材需要蒸煮也会消耗蒸汽",
            u"即 1蒸汽/s"
        ])

        # 消息设置
        Messages = {
            "Messages.Prefix": u"<gray>[ <gradient:#FF80FF:#00FFFF>JiuWu's Kitchen</gradient> ]</gray>",
            "Messages.Load": u"{Prefix} <green>欢迎使用 JiuWu's Kitchen! 版本 {Version} 已准备就绪!",
            "Messages.Reload.LoadPlugin": u"{Prefix} <green>JiuWu's Kitchen 已重新加载!",
            "Messages.Reload.LoadChoppingBoardRecipe": u"{Prefix} <green>已准备好 {Amount} 道砧板料理配方",
            "Messages.Reload.LoadWokRecipe": u"{Prefix} <green>已准备好 {Amount} 道炒锅料理配方",
            "Messages.Reload.LoadGrinderRecipe": u"{Prefix} <green>已准备好 {Amount} 道研磨机工序配方",
            "Messages.Reload.LoadSteamerRecipe": u"{Prefix} <green>已准备好 {Amount} 道蒸锅料理配方",
            "Messages.InvalidMaterial": u"{Prefix} <red>大厨，这个食材 {Material} 似乎不太对劲...",
            "Messages.NotStarted": u"<red>未开始!",
            "Messages.Completed": u"<green>已完成!",
            "Messages.WokTop": u"<gold>炒锅中的食材:",
            "Messages.WokContent": u" <gray>{ItemName} <dark_gray>× <yellow>{ItemAmount} <gray>翻炒次数: <yellow>{Count}",
            "Messages.WokDown": u"<gold>总计翻炒次数: <yellow>{Count}",
            "Messages.WokHeatControl": u"<gold>火候强度: <yellow>{Heat}级",
            "Messages.NoPermission": u"{Prefix} <red>大厨，你没有特殊的权限哦! ",
            "Messages.Title.CutHand.MainTitle": u"<red>哎哟! 切到手了! ",
            "Messages.Title.CutHand.SubTitle": u"<gray>小心刀具! 你受到了 <red>{Damage} <gray>点伤害",
            "Messages.Title.Scald.MainTitle": u"<red>沸沸沸! 烫烫烫! ",
            "Messages.Title.Scald.SubTitle": u"<gray>小心热锅! 你受到了 <red>{Damage} <gray>点伤害",
            "Messages.Title.Grinder.MainTitle": u"<green>研磨开始!",
            "Messages.Title.Grinder.SubTitle": u"<gray>请等待 <green>{Time} <gray>秒研磨时间",
            "Messages.ActionBar.TakeOffItem": u"<gray>提示: 空手轻点砧板可取下食材",
            "Messages.ActionBar.WokNoItem": u"<red>炒锅空空如也，快放些食材吧! ",
            "Messages.ActionBar.WokAddItem": u"<green>向炒锅中添加了 <white>{Material} <green>食材! ",
            "Messages.ActionBar.CutAmount": u"<gray>切菜进度: <green>{CurrentCount} <dark_gray>/ <green>{NeedCount}",
            "Messages.ActionBar.StirCount": u"<gray>翻炒次数: <green>{Count}",
            "Messages.ActionBar.ErrorRecipe": u"<red>哎呀，这道菜不是这么做的! 大厨再想想？",
            "Messages.ActionBar.FailureRecipe": u"<red>烹饪失败...食材浪费了，别灰心! ",
            "Messages.ActionBar.SuccessRecipe": u"<green>完美! 你成功烹饪了一道美味佳肴! ",
            "Messages.ActionBar.CannotCut": u"<red>大厨，这个食材不能在这里处理哦! ",
            "Messages.ActionBar.BurntFood": u"<red>哎呀! 火太大了，菜烧焦了! ",
            "Messages.ActionBar.RawFood": u"<red>哎呀! 菜还没熟透呢! ",
            "Messages.ActionBar.StirFriedTooQuickly": u"<red>翻炒得太急了! 食材还没熟透呢! ",
            "Messages.ActionBar.WokStirItem": u"<green>正在翻炒 <gray>{Material}...",
            "Messages.ActionBar.NoGrinderReplace": u"<red>这个东西太硬了，研磨机无法处理! ",
            "Messages.ActionBar.OnRunGrinder": u"<red>研磨机正在工作中! 请稍后再试! ",
            "Messages.ActionBar.SuccessGrinder": u"<green>研磨成功!",
            "Messages.ActionBar.AddFuel": u"<green>已添加燃料: <white>{Item} <dark_gray>| <green>剩余燃烧时间: <yellow>{Second}秒",
            "Messages.ActionBar.AddMoisture": u"<green>已添加物品: <aqua>{Item} <dark_gray>| <green>增加水份值: <aqua>{Moisture} <dark_gray>| <green>当前水份值: <blue>{Total}",
            "Messages.ActionBar.SteamerInfo": u"<gray>燃烧时间: <yellow>{BurningTime}</yellow>秒 | 水份: <aqua>{Moisture}</aqua> | 蒸汽: <white>{Steam}</white> | 烹饪进度: <yellow>{Progress}</gray>",
            "Messages.ActionBar.ChoppingBoardTooFast": u"<red>操作太快了! 请稍等片刻再继续!",
            "Messages.PluginLoad.CraftEngine": u"{Prefix} <green>检测到 CraftEngine 插件",
            "Messages.PluginLoad.MMOItems": u"{Prefix} <green>检测到 MMOItems 插件",
            "Messages.PluginLoad.PlaceholderAPI": u"{Prefix} <green>检测到 PlaceholderAPI 插件",
            "Messages.PluginLoad.NeigeItems": u"{Prefix} <green>检测到 NeigeItems 插件"
        }

        for KEY, VALUE in Messages.items(): ConfigManager.setConfigValue(configFile, KEY, VALUE)

        # 音效设置
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardAddItem", u"entity.item_frame.add_item", [u"砧板添加食材的音效"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardCutItem", u"item.axe.strip", [u"砧板切割食材的音效"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardCutHand", u"entity.player.hurt", [u"砧板切割时手被切伤的音效"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokAddItem", u"block.anvil.hit", [u"炒锅添加食材的音效"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokStirItem", u"block.lava.extinguish", [u"炒锅翻炒食材的音效"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokScald", u"entity.player.hurt_on_fire", [u"炒锅翻炒时手被烫伤的音效"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokTakeOffItem", u"entity.item.pickup", [u"炒锅取出食材的音效"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.GrinderStart", u"block.grindstone.use", [u"研磨机开始研磨的音效"])

        # 粒子设置
        ConfigManager.setConfigValue(
            configFile, "Setting.Particle.ChoppingBoardCutItem.Type", "CLOUD", [u"砧板切割食材的粒子"])
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.Amount", 10)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetX", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetY", 1.0)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetZ", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.Speed", 0.05)

        ConfigManager.setConfigValue(
            configFile, "Setting.Particle.WokStirItem.Type", "CAMPFIRE_COSY_SMOKE", [u"炒锅翻炒食材的粒子"])
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.Amount", 10)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetX", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetY", 1.0)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetZ", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.Speed", 0.05)

        ConfigManager.setConfigValue(
            configFile, "Setting.Particle.GrinderStart.Type", "GLOW", [u"研磨机开始研磨的粒子"])
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.Amount", 10)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.OffsetX", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.OffsetY", 1.0)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.OffsetZ", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.Speed", 0.05)

        configFile.save()
        return ps.config.loadConfig(configPath)

    @staticmethod
    def loadChoppingBoardRecipe():
        """加载砧板配方配置文件

        返回:
            对象: 砧板配方文件
        """
        choppingBoardRecipePath = "JiuWu's Kitchen/Recipe/ChoppingBoard.yml"
        return ps.config.loadConfig(choppingBoardRecipePath)

    @staticmethod
    def loadWokRecipe():
        """加载炒锅配方配置文件

        返回:
            对象: 砧板配方文件
        """
        wokRecipePath = "JiuWu's Kitchen/Recipe/Wok.yml"
        return ps.config.loadConfig(wokRecipePath)

    @staticmethod
    def loadSteamerRecipe():
        """加载蒸锅配方配置文件

        返回:
            对象: 蒸锅配方文件
        """
        steamerRecipePath = "JiuWu's Kitchen/Recipe/Steamer.yml"
        return ps.config.loadConfig(steamerRecipePath)

    @staticmethod
    def loadData():
        """加载数据文件

        返回:
            对象: 数据文件
        """
        dataPath = "JiuWu's Kitchen/Data.yml"
        return ps.config.loadConfig(dataPath)

    @staticmethod
    def loadGrinderRecipe():
        """加载研磨机配方配置文件

        返回:
            对象: 研磨机配方文件
        """
        grinderRecipePath = "JiuWu's Kitchen/Recipe/Grinder.yml"
        return ps.config.loadConfig(grinderRecipePath)

    @staticmethod
    def getConfig():
        """获取主配置对象"""
        if ConfigManager.config is None:
            ConfigManager.config = ConfigManager.loadConfig()
        return ConfigManager.config

    @staticmethod
    def getChoppingBoardRecipe():
        """获取砧板配方配置"""
        if ConfigManager.choppingBoardRecipe is None:
            ConfigManager.choppingBoardRecipe = ConfigManager.loadChoppingBoardRecipe()
        return ConfigManager.choppingBoardRecipe

    @staticmethod
    def getWokRecipe():
        """获取炒锅配方配置"""
        if ConfigManager.wokRecipe is None:
            ConfigManager.wokRecipe = ConfigManager.loadWokRecipe()
        return ConfigManager.wokRecipe

    @staticmethod
    def getGrinderRecipe():
        """获取研磨机配方配置"""
        if ConfigManager.grinderRecipe is None:
            ConfigManager.grinderRecipe = ConfigManager.loadGrinderRecipe()
        return ConfigManager.grinderRecipe
    
    @staticmethod
    def getSteamerRecipe():
        """获取蒸锅配方配置"""
        if ConfigManager.steamerRecipe is None:
            ConfigManager.steamerRecipe = ConfigManager.loadSteamerRecipe()
        return ConfigManager.steamerRecipe

    @staticmethod
    def getData():
        """获取数据文件"""
        if ConfigManager.data is None:
            ConfigManager.data = ConfigManager.loadData()
        return ConfigManager.data

    @staticmethod
    def getPrefix():
        """获取消息前缀"""
        if ConfigManager.prefix is None:
            ConfigManager.prefix = ConfigManager.getConfig().getString("Messages.Prefix")
        return ConfigManager.prefix

    @staticmethod
    def reloadAll():
        """重新加载所有配置文件"""
        ConfigManager.config = ConfigManager.loadConfig()
        ConfigManager.choppingBoardRecipe = ConfigManager.loadChoppingBoardRecipe()
        ConfigManager.wokRecipe = ConfigManager.loadWokRecipe()
        ConfigManager.grinderRecipe = ConfigManager.loadGrinderRecipe()
        ConfigManager.steamerRecipe = ConfigManager.loadSteamerRecipe()
        ConfigManager.data = ConfigManager.loadData()
        ConfigManager.prefix = None

class MiniMessageUtils:
    """MiniMessage工具类"""

    # 类常量
    MiniMessages = MiniMessage.miniMessage()
    GsonSerializer = GsonComponentSerializer.gson()
    PlainTextSerializer = PlainTextComponentSerializer.plainText()
    LegacySerializer = LegacyComponentSerializer.builder().hexColors().hexCharacter(u"#").character(u"&").build()

    @staticmethod
    def isString(MessageObj):
        """判断消息是否为字符串

        参数:
            MessageObj: 要检查的消息

        返回:
            bool: 是否为字符串
        """
        return isinstance(MessageObj, basestring)  # type: ignore

    @staticmethod
    def containsLegacyColors(TextStr):
        """检查文本是否包含传统颜色格式

        参数:
            TextStr: 要检查的文本

        返回:
            bool: 是否包含传统颜色格式
        """
        if not MiniMessageUtils.isString(TextStr):
            return False

        return "&" in TextStr and re.search(r"&[0-9a-fk-orA-FK-OR]", TextStr) is not None

    @staticmethod
    def convertLegacyToMiniMessage(TextStr):
        """将传统颜色代码转换为MiniMessage格式

        参数:
            TextStr: 包含传统颜色代码的文本

        返回:
            str: 转换后的MiniMessage格式文本
        """
        if not MiniMessageUtils.isString(TextStr) or not MiniMessageUtils.containsLegacyColors(TextStr):
            return TextStr
        ComponentObj = MiniMessageUtils.LegacySerializer.deserialize(TextStr)
        return MiniMessageUtils.MiniMessages.serialize(ComponentObj)

    @staticmethod
    def stringToComponent(TextStr):
        """将字符串转换为组件

        参数:
            TextStr: 要转换的文本

        返回:
            Component: 转换后的组件
        """
        if not MiniMessageUtils.isString(TextStr):
            return Component.empty()
        TextStr = MiniMessageUtils.convertLegacyToMiniMessage(TextStr)
        return MiniMessageUtils.MiniMessages.deserialize(TextStr)

    @staticmethod
    def jsonToComponent(JsonStr):
        """将JSON字符串转换为组件

        参数:
            JsonStr: JSON格式的字符串

        返回:
            Component: 转换后的组件
        """
        if not MiniMessageUtils.isString(JsonStr):
            return Component.empty()
        try:
            return MiniMessageUtils.GsonSerializer.deserialize(JsonStr)
        except Exception as e:
            return MiniMessageUtils.MiniMessages.deserialize(u"<red>JSON解析错误: " + str(e) + "</red>")

    @staticmethod
    def nbtToComponent(NbtStr):
        """将NBT字符串转换为组件

        参数:
            NbtStr: NBT格式的字符串

        返回:
            Component: 转换后的组件
        """
        if not MiniMessageUtils.isString(NbtStr):
            return Component.empty()
        try:
            return MiniMessageUtils.jsonToComponent(NbtStr)
        except:
            return MiniMessageUtils.stringToComponent(NbtStr)

    @staticmethod
    def replaceTextPlaceholders(TextStr, PlaceholdersDict):
        """替换字符串中的文本占位符

        参数:
            TextStr: 原始文本
            PlaceholdersDict: 占位符字典，如 {"Target": "Notch"}
        返回:
            str: 替换后的文本
        """
        if not MiniMessageUtils.isString(TextStr) or not isinstance(PlaceholdersDict, dict):
            return TextStr
        try:
            return TextStr.format(**PlaceholdersDict)
        except:
            for Placeholder, Replacement in PlaceholdersDict.iteritems():
                PlaceholderPattern = "{" + Placeholder + "}"
                TextStr = TextStr.replace(PlaceholderPattern, str(Replacement))

        return TextStr

    @staticmethod
    def replaceComponentPlaceholders(ComponentObj, PlaceholdersDict):
        """解析组件中的字符占位符 (使用更高效的组件替换方法)

        参数:
            ComponentObj: 原始组件
            PlaceholdersDict: 占位符字典

        返回:
            Component: 替换后的组件
        """
        if ComponentObj is None or not isinstance(PlaceholdersDict, dict):
            return ComponentObj
        for Placeholder, Replacement in PlaceholdersDict.iteritems():
            ReplacementComp = MiniMessageUtils.processMessage(Replacement, None)
            Config = TextReplacementConfig \
                .builder() \
                .matchLiteral("{" + Placeholder + "}") \
                .replacement(ReplacementComp) \
                .build()
            ComponentObj = ComponentObj.replaceText(Config)

        return ComponentObj

    @staticmethod
    def processMessage(MessageObj, PlaceholdersDict=None):
        """处理消息，根据类型转换为组件并替换占位符

        参数:
            MessageObj: 原始消息
            PlaceholdersDict: 占位符字典

        返回:
            Component: 处理后的组件
        """
        if MessageObj is None:
            return Component.empty()
        TextComp = None
        if MiniMessageUtils.isString(MessageObj):
            if MessageObj.strip().startswith("{") and MessageObj.strip().endswith("}"):
                try:
                    json.loads(MessageObj)
                    TextComp = MiniMessageUtils.jsonToComponent(MessageObj)
                except:
                    TextComp = MiniMessageUtils.stringToComponent(MessageObj)
            else:
                TextComp = MiniMessageUtils.stringToComponent(MessageObj)
        elif isinstance(MessageObj, Component):
            TextComp = MessageObj
        else:
            TextComp = MiniMessageUtils.stringToComponent(str(MessageObj))
        if PlaceholdersDict:
            TextComp = MiniMessageUtils.replaceComponentPlaceholders(TextComp, PlaceholdersDict)
        return TextComp

    @staticmethod
    def sendMessage(Target, MessageObj, PlaceholdersDict=None):
        """给玩家发送消息

        参数:
            Target: 目标玩家
            MessageObj: 消息内容(可以是字符串、组件或JSON)
            PlaceholdersDict: 可选的占位符字典
        """
        if MessageObj is None:
            return

        Comp = MiniMessageUtils.processMessage(MessageObj, PlaceholdersDict)
        Target.sendMessage(Comp)

    @staticmethod
    def sendTitle(Target, TitleStr, SubtitleStr, PlaceholdersDict=None, FadeIn=10, Stay=70, FadeOut=20):
        """给玩家发送标题

        参数:
            Target: 目标玩家
            TitleStr: 标题内容
            SubtitleStr: 副标题内容
            PlaceholdersDict: 可选的占位符字典
            FadeIn: 淡入时间(ticks)
            Stay: 停留时间(ticks)
            FadeOut: 淡出时间(ticks)
        """
        if not isinstance(Target, Player):
            return

        TitleComp = MiniMessageUtils.processMessage(
            TitleStr, PlaceholdersDict
            ) if TitleStr else Component.empty()
        SubtitleComp = MiniMessageUtils.processMessage(
            SubtitleStr,PlaceholdersDict
            ) if SubtitleStr else Component.empty()
        Times = Title.Times.times(
            Duration.ofMillis(FadeIn * 50),  # ticks转换为毫秒
            Duration.ofMillis(Stay * 50),
            Duration.ofMillis(FadeOut * 50)
        )
        TitleObj = Title.title(TitleComp, SubtitleComp, Times)
        Target.showTitle(TitleObj)

    @staticmethod
    def sendActionBar(Target, MessageObj, PlaceholdersDict=None):
        """给玩家发送动作栏消息

        参数:
            Target: 目标玩家
            MessageObj: 消息内容
            PlaceholdersDict: 可选的占位符字典
        """
        if not isinstance(Target, Player) or MessageObj is None:
            return
        Comp = MiniMessageUtils.processMessage(MessageObj, PlaceholdersDict)
        Target.sendActionBar(Comp)

    @staticmethod
    def playSound(Target, SoundStr, Volume=1.0, Pitch=1.0):
        """给玩家或位置播放声音

        参数:
            Target: 目标玩家或位置
            SoundStr: 声音类型 (命名空间键字符串或声音名称)
            Volume: 音量
            Pitch: 音调
        """
        if SoundStr is None: return
        if isinstance(Target, Location):
            location = Target
            world = location.getWorld()
            if world is None:
                return
        elif isinstance(Target, Player):
            location = Target.getLocation()
            world = location.getWorld()
        else:
            return
        SoundObj = None
        if isinstance(SoundStr, Sound):
            SoundObj = SoundStr
        elif isinstance(SoundStr, basestring):  # type: ignore
            try:
                if ":" in SoundStr:
                    namespace, key = SoundStr.split(":", 1)
                    namespaced_key = NamespacedKey(namespace, key)
                else:
                    namespaced_key = NamespacedKey.minecraft(SoundStr.lower())

                registry_sound = Registry.SOUNDS.get(namespaced_key)
                if registry_sound:
                    SoundObj = registry_sound
            except Exception:
                pass

        # 播放声音
        if SoundObj:
            if isinstance(Target, Player):
                Target.playSound(location, SoundObj, Volume, Pitch)
            else:
                world.playSound(location, SoundObj, Volume, Pitch)

Config = ConfigManager.getConfig()
Prefix = ConfigManager.getPrefix()
ChoppingBoardRecipe = ConfigManager.getChoppingBoardRecipe()
WokRecipe = ConfigManager.getWokRecipe()
GrinderRecipe = ConfigManager.getGrinderRecipe()
SteamerRecipe = ConfigManager.getSteamerRecipe()
Data = ConfigManager.getData()
Console = Bukkit.getServer().getConsoleSender()

CraftEngineAvailable = False
MMOItemsAvailable = False
PlaceholderAPIAvailable = False
NeigeItemsAvailable = False

def ServerPluginLoad():
    """
    在插件加载时检查CraftEngine和MMOItems插件是否可用，并注册相关事件监听器
    """
    global CraftEngineAvailable, MMOItemsAvailable, PlaceholderAPIAvailable
    CraftEngineAvailable = Bukkit.getPluginManager().isPluginEnabled("CraftEngine")
    if CraftEngineAvailable:
        MiniMessageUtils.sendMessage(Console,Config.getString("Messages.PluginLoad.CraftEngine"), {"Prefix": Prefix})
        from net.momirealms.craftengine.bukkit.api.event import (  # type: ignore
            CustomBlockInteractEvent,
            CustomBlockBreakEvent,
        )
        ps.listener.registerListener(InteractionCraftEngineBlock, CustomBlockInteractEvent)
        ps.listener.registerListener(BreakCraftEngineBlock, CustomBlockBreakEvent)
    MMOItemsAvailable = Bukkit.getPluginManager().isPluginEnabled("MMOItems")
    if MMOItemsAvailable:
        MiniMessageUtils.sendMessage(Console,Config.getString("Messages.PluginLoad.MMOItems"), {"Prefix": Prefix})
    PlaceholderAPIAvailable = Bukkit.getPluginManager().isPluginEnabled("PlaceholderAPI")
    if PlaceholderAPIAvailable:
        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.PluginLoad.PlaceholderAPI"), {"Prefix": Prefix})
    NeigeItemsAvailable = Bukkit.getPluginManager().isPluginEnabled("NeigeItems")
    if NeigeItemsAvailable:
        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.PluginLoad.NeigeItems"), {"Prefix": Prefix})

def InteractionVanillaBlock(Event): return EventHandler.handleInteraction(Event, "vanilla")

def InteractionCraftEngineBlock(Event): return EventHandler.handleInteraction(Event, "craftengine")

def BreakVanillaBlock(Event): return EventHandler.handleBreak(Event, "vanilla")

def BreakCraftEngineBlock(Event): return EventHandler.handleBreak(Event, "craftengine")

class EventHandler:
    """统一事件处理类"""

    @staticmethod
    def handleInteraction(Event, EventType):
        """处理交互事件"""
        try:
            # 处理砧板方块
            if ChoppingBoardInteraction(Event, EventType):  return True
            # 处理炒锅方块
            if WokInteraction(Event, EventType):  return True
            # 处理研磨机方块
            if GrinderInteraction(Event, EventType):  return True
            # 处理蒸锅方块
            if SteamerInteraction(Event, EventType):  return True
            return False
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, str(e))
            return False

    @staticmethod
    def handleBreak(Event, EventType):
        """处理破坏事件"""
        try:
            # 处理砧板方块
            if ChoppingBoardBreak(Event, EventType):  return True
            # 处理炒锅方块
            if WokBreak(Event, EventType):  return True
            # 处理研磨机方块
            if GrinderBreak(Event, EventType):  return True
            # 处理蒸锅方块和热源方块
            if SteamerBreak(Event, EventType):  return True
                
            return False
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, str(e))
            return False

class EventUtils:
    """事件工具类"""

    @staticmethod
    def getPlayer(Event, EventType):
        """获取事件中的玩家对象

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            对象: 玩家对象
        """
        if EventType == "vanilla": return Event.getPlayer()
        elif EventType == "craftengine": return Event.player()
        return None

    @staticmethod
    def getPermission(Player, PermissionNode):
        """获取事件中玩家对象的权限

        参数:
            Permissions: 权限字符串

        返回:
            bool: 是否拥有权限
        """
        if Player is None:
            return False
        if Player.isOp():
            return True
        return Player.hasPermission(PermissionNode)

    @staticmethod
    def getInteractionBlock(Event, EventType):
        """获取事件中的方块对象

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            对象: 方块对象
        """
        if EventType == "vanilla": return Event.getClickedBlock()
        elif EventType == "craftengine": return Event.bukkitBlock()
        return None

    @staticmethod
    def getBreakBlock(Event, EventType):
        """获取事件中的方块对象

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            对象: 方块对象
        """
        if EventType == "vanilla": return Event.getBlock()
        elif EventType == "craftengine": return Event.bukkitBlock()
        return None

    @staticmethod
    def getAction(Event, EventType):
        """获取事件中的动作类型

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            对象: 动作类型
        """
        if EventType == "vanilla": return Event.getAction()
        elif EventType == "craftengine": return Event.action()
        return None

    @staticmethod
    def getHand(Event, EventType):
        """获取事件中的手

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            对象: 手
        """
        if EventType == "vanilla": return Event.getHand()
        elif EventType == "craftengine": return Event.hand()
        return None

    @staticmethod
    def isMainHand(Event, EventType):
        """判断事件是否为主手

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            bool: 是否为主手
        """
        if EventType == "vanilla": return Event.getHand() == EquipmentSlot.HAND
        elif EventType == "craftengine":
            from net.momirealms.craftengine.core.entity.player import InteractionHand  # type: ignore
            return Event.hand() == InteractionHand.MAIN_HAND

    def isOffHand(Event, EventType):
        """判断事件是否为副手

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            bool: 是否为副手
        """
        if EventType == "vanilla": return Event.getHand() == EquipmentSlot.OFF_HAND
        elif EventType == "craftengine":
            from net.momirealms.craftengine.core.entity.player import InteractionHand  # type: ignore
            return Event.hand() == InteractionHand.OFF_HAND

    @staticmethod
    def isLeftClick(Event, EventType):
        """判断事件是否为左键点击

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            bool: 是否为左键点击
        """
        if EventType == "vanilla": return Event.getAction() == Action.LEFT_CLICK_BLOCK
        elif EventType == "craftengine": return Event.action() == Event.Action.LEFT_CLICK
        return False

    @staticmethod
    def isRightClick(Event, EventType):
        """判断事件是否为右键点击

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)

        返回:
            bool: 是否为右键点击
        """
        if EventType == "vanilla": return Event.getAction() == Action.RIGHT_CLICK_BLOCK
        elif EventType == "craftengine": return Event.action() == Event.Action.RIGHT_CLICK
        return False

    @staticmethod
    def isSneaking(EventPlayer, ConfigType):
        """判断事件是否为潜行状态

        参数:
            EventPlayer: 玩家对象
            ConfigType: 配置类型 (vanilla或craftengine)

        返回:
            bool: 是否为潜行状态
        """
        SneakingStatus = Config.getBoolean("Setting." + ConfigType + ".StealthInteraction")
        if SneakingStatus and not EventPlayer.isSneaking(): return False
        elif not SneakingStatus and EventPlayer.isSneaking(): return False
        else: return True

    @staticmethod
    def isTargetBlock(Block, Target):
        """判断方块是否为目标方块

        参数:
            Block: 方块对象
            Target: 目标类型

        返回:
            bool: 是否为目标方块
        """
        MaterialSetting = Config.getString("Setting." + Target + ".Material")
        if Config.getBoolean("Setting." + Target + ".Custom"):
            if " " in MaterialSetting:
                Identifier, ID = MaterialSetting.split(" ", 1)
                if Identifier == "craftengine":
                    try:
                        from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
                        ClickBlockState = CraftEngineBlocks.getCustomBlockState(Block)
                        if ClickBlockState is not None and str(ClickBlockState) == ID: 
                            return True
                    except: 
                        return False
            return False
        else:
            if " " in MaterialSetting:
                namespace, materialName = MaterialSetting.split(" ", 1)
                if namespace == "minecraft":
                    try:
                        return Block.getType() == Material.valueOf(materialName.upper())
                    except: 
                        return False
            else:
                try:
                    return Block.getType() == Material.valueOf(MaterialSetting.upper())
                except: 
                    return False

    @staticmethod
    def setCancelled(Event, EventType, Cancelled):
        """设置事件是否被取消

        参数:
            Event: 事件对象
            EventType: 事件类型 (vanilla或craftengine)
            Cancelled: 是否取消 (True或False)

        返回:
            bool: 是否取消
        """
        if EventType == "vanilla": Event.setCancelled(Cancelled)
        elif EventType == "craftengine": Event.setCancelled(Cancelled)

    @staticmethod
    def sendParticle(TatgetType, SendLocation):
        """发送粒子"""
        ParticleType = Config.getString("Setting.Particle." +  TatgetType + ".Type")
        ParticleAmount = Config.getInt("Setting.Particle." +  TatgetType + ".Amount")
        ParticleoffsetX = Config.getDouble("Setting.Particle." +  TatgetType + ".OffsetX")
        ParticleoffsetY = Config.getDouble("Setting.Particle." +  TatgetType + ".OffsetY")
        ParticleoffsetZ = Config.getDouble("Setting.Particle." +  TatgetType + ".OffsetZ")
        ParticleSpeed = Config.getDouble("Setting.Particle." +  TatgetType + ".Speed")
        try: ParticleType = Particle.valueOf(ParticleType)
        except: ParticleType = Particle.valueOf("CLOUD")
        try:
            SendLocation.getWorld().spawnParticle(
                ParticleType,
                SendLocation,
                ParticleAmount,
                ParticleoffsetX,
                ParticleoffsetY,
                ParticleoffsetZ,
                ParticleSpeed)
        except: pass

class ToolUtils:
    """工具类"""

    # 类常量
    CRAFTENGINE = "craftengine"
    MMOITEMS = "mmoitems"
    MINECRAFT = "minecraft"
    NEIGEITEMS = "neigeitems"

    @staticmethod
    def parseAndExecuteCommand(CommandStr, ExecutePlayer=None, Chance=100, ExecuteCount=1):
        """解析并执行命令奖励

        参数:
            CommandStr: 命令字符串，格式为 "command <命令内容> a:<执行次数> c:<概率>"
            ExecutePlayer: 可选的玩家对象，用于解析占位符
            Chance: 默认概率 (如果命令字符串中未指定)
            ExecuteCount: 默认执行次数 (如果命令字符串中未指定)

        返回:
            bool: 是否成功执行了命令
        """
        try:
            if not CommandStr.startswith("command "):
                return False
            CommandContent = CommandStr[8:]
            Parts = CommandContent.split(" ")
            ActualCommand = []
            ActualChance = Chance
            ActualExecuteCount = ExecuteCount
            for Part in Parts:
                if Part.startswith("a:"):
                    try:
                        ActualExecuteCount = int(Part[2:])
                    except ValueError:
                        pass
                elif Part.startswith("c:"):
                    try:
                        ActualChance = int(Part[2:])
                    except ValueError:
                        pass
                else:
                    ActualCommand.append(Part)
            if random.randint(1, 100) > ActualChance:
                return False
            FinalCommand = " ".join(ActualCommand)
            if ExecutePlayer:
                FinalCommand = FinalCommand.replace("%player%", ExecutePlayer.getName())
            if PlaceholderAPIAvailable and ExecutePlayer:
                try:
                    from me.clip.placeholderapi.PlaceholderAPI import setPlaceholders  # type: ignore
                    FinalCommand = setPlaceholders(ExecutePlayer, FinalCommand)
                except Exception as e:
                    MiniMessageUtils.sendMessage(Console, u"PAPI占位符解析错误: " + str(e))
            for i in range(ActualExecuteCount):
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), FinalCommand)
            return True
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, u"命令解析错误: " + str(e))
            return False

    @staticmethod
    def processReward(RewardStr, RewardPlayer=None):
        """处理奖励字符串，可以是物品或命令"""
        if RewardStr.startswith("command "):
            return ToolUtils.parseAndExecuteCommand(RewardStr, RewardPlayer)
        try:
            parts = RewardStr.split(" ")
            if len(parts) < 4:
                return False
            ItemNamespace = parts[0]  # 使用minecraft命名空间
            ItemId = parts[1]
            AmountRange = parts[2]
            Chance = int(parts[3])
            if random.randint(1, 100) > Chance:
                return False
            if "-" in AmountRange:
                MinAmount, MaxAmount = map(int, AmountRange.split("-"))
                Amount = random.randint(MinAmount, MaxAmount)
            else:
                Amount = int(AmountRange)
            ItemKey = "{} {}".format(ItemNamespace, ItemId)  # 使用空格分隔的格式
            ResultItemStack = ToolUtils.createItemStack(ItemKey, Amount)
            if not ResultItemStack:
                MiniMessageUtils.sendMessage(Console, Config.getString("Messages.InvalidMaterial"),
                                    {"Prefix": Prefix, "Material": ItemKey})
                return False
            if Config.getBoolean("Setting.ChoppingBoard.Drop"):
                DropLocation = RewardPlayer.getLocation() if RewardPlayer else None
                if DropLocation:
                    ItemEntity = DropLocation.getWorld().dropItem(DropLocation, ResultItemStack)
                    ItemEntity.setPickupDelay(20)
            elif RewardPlayer:
                GiveItemToPlayer(RewardPlayer, ResultItemStack)
            return True
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, u"物品奖励解析错误: " + str(e))
            return False

    @staticmethod
    def isBlockMaterialType(Item):
        """判断物品是否为方块材质

        参数:
            Item: 物品对象

        返回:
            str: 材质类型
        """
        if Item is None: return "Item"
        ItemType = Item.getType()
        if ItemType.isBlock(): return "Block"
        else: return "Item"

    @staticmethod
    def isToolItem(Item, Config, Type, Tool, material=None):
        """判断物品是否为指定的工具类型"""
        if not Item or Item.getType() == Material.AIR:
            return False
        if material is not None:
            materialToCheck = material
        else:
            materials = ToolUtils.getToolMaterials(Config, Type, Tool)
            materialToCheck = materials[0] if materials else None
        if materialToCheck is None:
            return False
        itemIdentifier = ToolUtils.getItemIdentifier(Item)
        CustomSetting = Config.getBoolean("Setting." + Type + "." + Tool + ".Custom")
        if CustomSetting:
            return itemIdentifier == materialToCheck
        else:
            try:
                materialName = materialToCheck
                if " " in materialToCheck:
                    parts = materialToCheck.split(" ")
                    if len(parts) >= 2:
                        if parts[0].lower() == "minecraft":
                            materialName = parts[1]
                        else:
                            return False
                elif ":" in materialToCheck:
                    parts = materialToCheck.split(":")
                    if len(parts) >= 2:
                        if parts[0].lower() == "minecraft":
                            materialName = parts[1]
                        else:
                            return False
                materialName = materialName.upper()
                return Item.getType() == Material.valueOf(materialName)
            except:
                return False
    
    @staticmethod
    def getToolMaterials(Config, Type, Tool):
        """获取指定工具的材料列表
        
        参数:
            Config: 配置对象
            Type: 工具类型
            Tool: 工具名称
            
        返回:
            list: 材料列表
        """
        return Config.getStringList("Setting." + Type + "." + Tool + ".Material")

    @staticmethod
    def isCraftEngineItem(Item, ExpectedID):
        """检查是否为指定ID的CraftEngine物品

        参数:
            Item: 物品对象
            ExpectedID: 期望的ID

        返回:
            bool: 是否为指定ID的CraftEngine物品
        """
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            if CraftEngineItems.isCustomItem(Item):
                ItemId = CraftEngineItems.getCustomItemId(Item)
                return str(ItemId) == ExpectedID
        except Exception: return False

    @staticmethod
    def isMMOItemsItem(Item, ExpectedID):
        """检查是否为指定ID的MMOItems物品

        参数:
            Item: 物品对象
            ExpectedID: 期望的ID

        返回:
            bool: 是否为指定ID的MMOItems物品
        """
        try:
            from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
            NbtItem = NBTItem.get(Item)
            if NbtItem.hasType():
                ItemType = NbtItem.getType()
                ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                CombinedId = str(ItemType) + ":" + str(ItemId)
                return CombinedId == ExpectedID
        except Exception: return False

    @staticmethod
    def getItemIdentifier(Item):
        """获取物品的唯一标识符字符串

        参数:
            Item: 物品对象

        返回:
            str: 标识符字符串
        """
        if not Item or Item.getType() == Material.AIR:
            return "AIR"
        
        # 检查CraftEngine物品
        if CraftEngineAvailable:
            craftEngineId = ToolUtils.getCraftEngineItemId(Item)
            if craftEngineId: 
                return ToolUtils.CRAFTENGINE + " " + str(craftEngineId)
        
        # 检查MMOItems物品
        if MMOItemsAvailable:
            mmoItemsId = ToolUtils.getMMOItemsItemId(Item)
            if mmoItemsId: 
                return ToolUtils.MMOITEMS + " " + mmoItemsId

        # 检查NeigeItems物品
        if NeigeItemsAvailable:
            neigeItemsId = ToolUtils.getNeigeItemsItemId(Item)
            if neigeItemsId: 
                return ToolUtils.NEIGEITEMS + " " + str(neigeItemsId)
        
        # 默认返回原版物品标识
        return ToolUtils.MINECRAFT + " " + Item.getType().name()

    @staticmethod
    def getCraftEngineItemId(Item):
        """获取CraftEngine物品ID

        参数:
            Item: 物品对象

        返回:
            str: 物品ID
        """
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            if CraftEngineItems.isCustomItem(Item): return CraftEngineItems.getCustomItemId(Item)
        except Exception: return None

    @staticmethod
    def getMMOItemsItemId(Item):
        """获取MMOItems物品ID

        参数:
            Item: 物品对象

        返回:
            str: 物品ID
        """
        try:
            from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
            NbtItem = NBTItem.get(Item)
            if NbtItem.hasType():
                ItemType = NbtItem.getType()
                ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                return str(ItemType) + ":" + str(ItemId)
        except Exception: return None
    
    @staticmethod
    def getNeigeItemsItemId(Item):
        """获取NeigeItems物品ID

        参数:
            Item: 物品对象

        返回:
            str: 物品ID
        """
        try:
            from pers.neige.neigeitems.utils.ItemUtils import ItemUtils  # type: ignore
            itemInfo = ItemUtils.isNiItem(Item)
            if itemInfo:
                return itemInfo.getId()
        except Exception: 
            return None
        return None

    @staticmethod
    def createItemStack(ItemKey, Amount=1):
        """创建物品栈"""
        if not ItemKey: return None
        Parts = ItemKey.split(" ")
        if len(Parts) < 1: return None
        ItemType = Parts[0]
        if ItemType == ToolUtils.NEIGEITEMS and NeigeItemsAvailable:
            return ToolUtils.createNeigeItemsItem(Parts, Amount)
        elif ItemType == ToolUtils.MINECRAFT: 
            return ToolUtils.createMinecraftItem(Parts, Amount)
        elif ItemType == ToolUtils.CRAFTENGINE and CraftEngineAvailable:
            return ToolUtils.createCraftEngineItem(Parts, Amount)
        elif ItemType == ToolUtils.MMOITEMS and MMOItemsAvailable: 
            return ToolUtils.createMMOItemsItem(Parts, Amount)
        else:
            try:
                Item = Material.valueOf(ItemType.upper())
                return ItemStack(Item, Amount)
            except: 
                try:
                    minecraftKey = ToolUtils.MINECRAFT + " " + ItemType
                    return ToolUtils.createMinecraftItem([ToolUtils.MINECRAFT, ItemType], Amount)
                except: 
                    return None

    @staticmethod
    def createMinecraftItem(Parts, Amount):
        """创建原版Minecraft物品

        参数:
            Parts: 物品键分割后的列表
            Amount: 数量

        返回:
            ItemStack: 物品栈
        """
        try:
            if len(Parts) > 1: Item = Material.valueOf(Parts[1])
            else: Item = Material.valueOf(Parts[0])
            return ItemStack(Item, Amount)
        except: return None

    @staticmethod
    def createCraftEngineItem(Parts, Amount):
        """创建CraftEngine物品

        参数:
            Parts: 物品键分割后的列表
            Amount: 数量

        返回:
            ItemStack: 物品栈
        """
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
            from net.momirealms.craftengine.core.util import Key  # type: ignore
            if len(Parts) > 1:
                KeyParts = Parts[1].split(":")
                if len(KeyParts) >= 2:
                    CraftEngineItem = CraftEngineItems.byId(Key(KeyParts[0], KeyParts[1])).buildItemStack()
                    CraftEngineItem.setAmount(Amount)
                    return CraftEngineItem
        except Exception: 
            return None
        return None

    @staticmethod
    def createMMOItemsItem(Parts, Amount):
        """创建MMOItems物品

        参数:
            Parts: 物品键分割后的列表
            Amount: 数量

        返回:
            ItemStack: 物品栈
        """
        try:
            from net.Indyuce.mmoitems import MMOItems  # type: ignore
            if len(Parts) > 1:
                IdParts = Parts[1].split(":")
                if len(IdParts) >= 2:
                    MMOItemsItem = MMOItems.plugin.getMMOItem(
                        MMOItems.plugin.getTypes().get(IdParts[0]), IdParts[1]
                        ).newBuilder().build()
                    MMOItemsItem.setAmount(Amount)
                    return MMOItemsItem
        except Exception: 
            return None
        return None

    @staticmethod
    def createNeigeItemsItem(Parts, Amount):
        """创建NeigeItems物品

        参数:
            Parts: 物品键分割后的列表
            Amount: 数量

        返回:
            ItemStack: 物品栈
        """
        try:
            from pers.neige.neigeitems.manager.ItemManager import ItemManager  # type: ignore
            if len(Parts) > 1:
                itemId = Parts[1]
                if ItemManager.hasItem(itemId):
                    itemStack = ItemManager.getItemStack(itemId, None, None)
                    if itemStack:
                        itemStack.setAmount(Amount)
                        return itemStack
        except Exception as e:
            return None
        return None

    @staticmethod
    def getItemDisplayName(Item):
        """获取物品的显示名称

        参数:
            Item: 物品对象
        返回:
            显示名称字符串或组件
        """
        # 检查CraftEngine物品
        if CraftEngineAvailable:
            try:
                from net.momirealms.craftengine.bukkit.api import CraftEngineItems  # type: ignore
                from net.momirealms.craftengine.bukkit.item import BukkitItemManager  # type: ignore
                if CraftEngineItems.isCustomItem(Item):
                    return BukkitItemManager.instance().wrap(Item).hoverNameJson().get()
            except Exception: pass
        # 检查MMOItems物品
        if MMOItemsAvailable:
            try:
                from io.lumine.mythic.lib.api.item import NBTItem  # type: ignore
                NbtItem = NBTItem.get(Item)
                if NbtItem.hasType(): return NbtItem.getString("MMOITEMS_NAME")
            except Exception: pass
        # 检查NeigeItems物品
        if NeigeItemsAvailable:
            try:
                from pers.neige.neigeitems.utils.ItemUtils import ItemUtils  # type: ignore
                return ItemUtils.getItemName(Item)
            except Exception: 
                pass
        # 默认返回原版物品名称
        return Component.translatable(Item.translationKey())

def ChoppingBoardBreak(Event, EventType):
    """砧板破坏事件处理"""
    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if not EventUtils.isTargetBlock(BreakBlock, "ChoppingBoard"): return False
    FileKey = GetFileKey(BreakBlock)
    hasExistingDisplay = Data.contains("ChoppingBoard." + FileKey + ".CutCount")
    if not hasExistingDisplay: return False
    DisplayLocation = CalculateDisplayLocation(BreakBlock, "ChoppingBoard")
    ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)
    if not ItemDisplayEntity: return False
    ItemDisplayEntity = ItemDisplayEntity[0]
    DisplayItem = ItemDisplayEntity.getItemStack()
    if not DisplayItem: return False
    ItemEntity = BreakBlock.getWorld().dropItem(DisplayLocation, DisplayItem)
    ItemEntity.setPickupDelay(0)
    Data.set("ChoppingBoard." + FileKey, None)
    Data.save()
    ItemDisplayEntity.remove()
    return True

def WokBreak(Event, EventType):
    """炒锅破坏事件处理"""
    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if not EventUtils.isTargetBlock(BreakBlock, "Wok"): return False
    FileKey = GetFileKey(BreakBlock)
    hasExistingDisplay = Data.contains("Wok." + FileKey)
    if not hasExistingDisplay: return False
    DisplayLocation = CalculateDisplayLocation(BreakBlock, "Wok")
    ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)
    if not ItemDisplayEntity: return False
    for Display in ItemDisplayEntity:
        if Display and not Display.isDead():
            DisplayItem = Display.getItemStack()
            if not DisplayItem: return False
            ItemEntity = BreakBlock.getWorld().dropItem(Display.getLocation(), DisplayItem)
            ItemEntity.setPickupDelay(0)
            Display.remove()
    Data.set("Wok." + FileKey, None)
    Data.save()
    return True

def GrinderBreak(Event, EventType):
    """研磨机破坏事件处理"""
    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if not EventUtils.isTargetBlock(BreakBlock, "Grinder"): return False
    FileKey = GetFileKey(BreakBlock)
    hasExistingGrinder = Data.contains("Grinder." + FileKey)
    if not hasExistingGrinder: return False
    InputItem = Data.getString("Grinder." + FileKey + ".Input")
    if InputItem:
        InputItemStack = ToolUtils.createItemStack(InputItem)
        if InputItemStack:
            DropLocation = BreakBlock.getLocation().add(0.5, 1.0, 0.5)
            ItemEntity = BreakBlock.getWorld().dropItem(DropLocation, InputItemStack)
            ItemEntity.setPickupDelay(0)
    Data.set("Grinder." + FileKey, None)
    Data.save()
    return True

def SteamerBreak(Event, EventType):
    """蒸锅破坏事件处理"""
    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if EventUtils.isTargetBlock(BreakBlock, "Steamer"):
        return HandleSteamerBlockBreak(BreakBlock)
    elif isHeatSourceBlock(BreakBlock):
        return HandleHeatSourceBlockBreak(BreakBlock)
    return False

def HandleSteamerBlockBreak(SteamerBlock):
    """处理蒸锅方块的破坏"""
    try:
        FileKey = GetFileKey(SteamerBlock)
        SteamerDataPath = "Steamer." + FileKey
        if not Data.contains(SteamerDataPath):
            return False
        ExtinguishHeatSource(FileKey)
        DropSteamerItems(SteamerBlock, FileKey)
        Data.set(SteamerDataPath, None)
        Data.save()
        CleanupSteamerTempData(FileKey)
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def HandleHeatSourceBlockBreak(HeatSourceBlock):
    """处理热源方块的破坏"""
    try:
        TopBlock = HeatSourceBlock.getRelative(BlockFace.UP)
        if not EventUtils.isTargetBlock(TopBlock, "Steamer"):
            return False
        return HandleSteamerBlockBreak(TopBlock)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def DropSteamerItems(SteamerBlock, FileKey):
    """掉落蒸锅中的所有物品"""
    try:
        SlotsPath = "Steamer." + FileKey + ".Slots"
        CookingProgressPath = "Steamer." + FileKey + ".CookingProgress"
        if not Data.contains(SlotsPath):
            return
        SlotItems = Data.getStringList(SlotsPath)
        CookingProgress = []
        if Data.contains(CookingProgressPath):
            CookingProgress = Data.getIntegerList(CookingProgressPath)
        if len(CookingProgress) < len(SlotItems):
            CookingProgress.extend([0] * (len(SlotItems) - len(CookingProgress)))
        DropLocation = SteamerBlock.getLocation().add(0.5, 1.0, 0.5)
        for i, itemIdentifier in enumerate(SlotItems):
            if itemIdentifier != "AIR":
                try:
                    CurrentProgress = CookingProgress[i] if i < len(CookingProgress) else 0
                    if SteamerRecipe.contains(itemIdentifier):
                        requiredSteam = SteamerRecipe.getInt(itemIdentifier + ".Steam", 0)
                        outputItem = SteamerRecipe.getString(itemIdentifier + ".Output")
                        if outputItem and CurrentProgress >= requiredSteam:
                            itemToDrop = outputItem
                        else:
                            itemToDrop = itemIdentifier
                    else:
                        for recipeKey in SteamerRecipe.getKeys(False):
                            outputItem = SteamerRecipe.getString(recipeKey + ".Output")
                            if outputItem and outputItem == itemIdentifier:
                                itemToDrop = itemIdentifier
                                break
                        else:
                            itemToDrop = itemIdentifier
                    itemStack = ToolUtils.createItemStack(itemToDrop, 1)
                    if itemStack:
                        itemEntity = SteamerBlock.getWorld().dropItem(DropLocation, itemStack)
                        itemEntity.setPickupDelay(20)
                except Exception as e:
                    MiniMessageUtils.sendMessage(Console, str(e))
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def CleanupSteamerTempData(FileKey):
    """清理蒸锅的临时数据"""
    try:
        players_to_remove = []
        for player_uuid, steamer_data in SteamerTempData.items():
            if steamer_data.get("steamerKey") == FileKey:
                players_to_remove.append(player_uuid)
        for player_uuid in players_to_remove:
            if player_uuid in SteamerTempData:
                del SteamerTempData[player_uuid]
            if player_uuid in SteamerInventories:
                del SteamerInventories[player_uuid]
        if FileKey in SteamerProcessingData:
            del SteamerProcessingData[FileKey]
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def ChoppingBoardInteraction(Event, EventType):
    """砧板交互事件处理"""
    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    if not ClickBlock: return False
    FileKey = GetFileKey(ClickBlock)
    ChoppingBoardDelay = Config.getDouble("Setting.ChoppingBoard.Delay", 1.0)
    if ChoppingBoardDelay > 0:
        LastInteractTime = Data.getLong("ChoppingBoard." + FileKey + ".LastInteractTime", 0)
        CurrentTime = System.currentTimeMillis()
        if CurrentTime - LastInteractTime < ChoppingBoardDelay * 1000:
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.ChoppingBoardTooFast"))
            EventUtils.setCancelled(Event, EventType, True)
            return True
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    if not EventUtils.isMainHand(Event, EventType): return False
    if EventUtils.isRightClick(Event, EventType):
        DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
        NearbyDisplay = FindNearbyDisplay(DisplayLocation)
        if NearbyDisplay:
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.TakeOffItem"))
            EventUtils.setCancelled(Event, EventType, True)
    if not EventUtils.isLeftClick(Event, EventType): return False
    if not EventUtils.isTargetBlock(ClickBlock, "ChoppingBoard"): return False
    if not EventUtils.isSneaking(ClickPlayer, "ChoppingBoard"): return False
    if Config.getBoolean("Setting.ChoppingBoard.SpaceRestriction"):
        if ClickBlock.getRelative(BlockFace.UP).getType() != Material.AIR: return False
    if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.choppingboard.interaction"):
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        EventUtils.setCancelled(Event, EventType, True)
        return False
    Data.set("ChoppingBoard." + FileKey + ".LastInteractTime", System.currentTimeMillis())
    hasExistingDisplay = Data.contains("ChoppingBoard." + FileKey + ".CutCount")
    if MainHandItem and MainHandItem.getType() != Material.AIR:
        if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.choppingboard.cut"):
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
            EventUtils.setCancelled(Event, EventType, True)
            return False
        if hasExistingDisplay:
            ToolMaterials = ToolUtils.getToolMaterials(Config, "ChoppingBoard", "KitchenKnife")
            isToolValid = False
            for material in ToolMaterials:
                if ToolUtils.isToolItem(MainHandItem, Config, "ChoppingBoard", "KitchenKnife", material):
                    isToolValid = True
                    break
            if isToolValid:
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
                ItemDisplayEntities = FindNearbyDisplay(DisplayLocation)
                if not ItemDisplayEntities: 
                    return False
                ItemDisplayEntity = ItemDisplayEntities[0]
                DisplayItem = ItemDisplayEntity.getItemStack()
                if not DisplayItem: 
                    return False
                ItemMaterial = ToolUtils.getItemIdentifier(DisplayItem)
                RequiredCuts = ChoppingBoardRecipe.getInt(ItemMaterial + ".Count")
                ReplacePermission = ChoppingBoardRecipe.getString(ItemMaterial + ".Permission")
                if ReplacePermission and not EventUtils.getPermission(ClickPlayer, ReplacePermission):
                    EventUtils.setCancelled(Event, EventType, True)
                    MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                    return False
                ResultMaterials = ChoppingBoardRecipe.getStringList(ItemMaterial + ".Output")
                if not RequiredCuts or RequiredCuts == 0:
                    EventUtils.setCancelled(Event, EventType, True)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.CannotCut"))
                    return False
                RemoveDurability = ChoppingBoardRecipe.getInt(ItemMaterial + ".Durability")
                RemoveDurability = 1 if RemoveDurability == 0 else RemoveDurability
                MainHandItem.setDurability(MainHandItem.getDurability() + RemoveDurability)
                ClickPlayer.getInventory().setItemInMainHand(MainHandItem)
                CurrentCuts = Data.getInt("ChoppingBoard." + FileKey + ".CutCount", 0)
                CurrentCuts += 1
                Data.set("ChoppingBoard." + FileKey + ".CutCount", CurrentCuts)
                Data.save()
                ParticleLocation = ClickBlock.getLocation().add(0.5, 1.1, 0.5)
                EventUtils.sendParticle("ChoppingBoardCutItem", ParticleLocation)
                DamageChance = None
                DamageValue = None
                RecipeDamagePath = ItemMaterial + ".Damage"
                if ChoppingBoardRecipe.contains(RecipeDamagePath):
                    DamageChance = ChoppingBoardRecipe.getInt(RecipeDamagePath + ".Chance")
                    DamageValue = ChoppingBoardRecipe.getInt(RecipeDamagePath + ".Value")
                elif Config.getBoolean("Setting.ChoppingBoard.Damage.Enable"):
                    DamageChance = Config.getInt("Setting.ChoppingBoard.Damage.Chance")
                    DamageValue = Config.getInt("Setting.ChoppingBoard.Damage.Value")
                if DamageChance is not None and DamageValue is not None:
                    if random.randint(1, 100) <= DamageChance:
                        ClickPlayer.damage(DamageValue)
                        MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardCutHand"))
                        MiniMessageUtils.sendTitle(ClickPlayer, Config.getString("Messages.Title.CutHand.MainTitle"),
                            Config.getString("Messages.Title.CutHand.SubTitle"), {"Damage": str(DamageValue)})
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.CutAmount"),
                    {"CurrentCount": str(CurrentCuts), "NeedCount": str(RequiredCuts)})
                MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardCutItem"))
                if CurrentCuts >= RequiredCuts:
                    if ResultMaterials and len(ResultMaterials) > 0:
                        for ResultMaterial in ResultMaterials:
                            ToolUtils.processReward(ResultMaterial, ClickPlayer)
                    ItemDisplayEntity.remove()
                    Data.set("ChoppingBoard." + FileKey, None)
                    Data.save()
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                EventUtils.setCancelled(Event, EventType, True)
                return True
            else:
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.TakeOffItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return False
        else:
            DisplayItem = MainHandItem.clone()
            DisplayItem.setAmount(1)
            if MainHandItem.getAmount() > 1:
                MainHandItem.setAmount(MainHandItem.getAmount() - 1)
                ClickPlayer.getInventory().setItemInMainHand(MainHandItem)
            else: 
                ClickPlayer.getInventory().setItemInMainHand(None)
            DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
            CreateItemDisplay(DisplayLocation, DisplayItem, "ChoppingBoard")
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardAddItem"))
            if not Data.contains("ChoppingBoard." + FileKey + ".CutCount"):
                Data.set("ChoppingBoard." + FileKey + ".CutCount", 0)
                Data.set("ChoppingBoard." + FileKey + ".LastInteractTime", System.currentTimeMillis())
                Data.save()
            EventUtils.setCancelled(Event, EventType, True)
            return True
    elif not MainHandItem or MainHandItem.getType() == Material.AIR:
        if hasExistingDisplay:
            DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
            ItemDisplayEntities = FindNearbyDisplay(DisplayLocation)
            if not ItemDisplayEntities: 
                return False
            ItemDisplayEntity = ItemDisplayEntities[0]
            DisplayItem = ItemDisplayEntity.getItemStack()
            if DisplayItem: 
                ClickPlayer.getInventory().setItemInMainHand(DisplayItem.clone())
            ItemDisplayEntity.remove()
            Data.set("ChoppingBoard." + FileKey, None)
            Data.save()
            EventUtils.setCancelled(Event, EventType, True)
            return True
    return False

def WokInteraction(Event, EventType):
    """
    处理炒锅的交互事件

    参数:
        Event: 事件对象
        EventType: 事件类型 ("vanilla" 或 "craftengine")
    """
    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    if not ClickBlock: return False
    ItemList = []
    if not EventUtils.isMainHand(Event, EventType): return False
    if not EventUtils.isTargetBlock(ClickBlock, "Wok"): return False
    FileKey = GetFileKey(ClickBlock)
    HeatLevel = 0
    BottomBlock = ClickBlock.getRelative(BlockFace.DOWN)
    BottomBlockType = BottomBlock.getType().name()
    HeatControl = Config.get("Setting.Wok.HeatControl").getKeys(False)
    if CraftEngineAvailable:
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
            if CraftEngineBlocks.isCustomBlock(BottomBlock):
                BottomBlockState = CraftEngineBlocks.getCustomBlockState(BottomBlock)
                CraftEngineKey = "craftengine " + str(BottomBlockState)
                if CraftEngineKey in HeatControl:
                    HeatLevel = Config.getInt("Setting.Wok.HeatControl." + CraftEngineKey)
        except:  pass
    if BottomBlockType in HeatControl: 
        HeatLevel = Config.getInt("Setting.Wok.HeatControl." + BottomBlockType)
    if not EventUtils.isSneaking(ClickPlayer, "Wok"): return False
    if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.wok.interaction"):
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        EventUtils.setCancelled(Event, EventType, True)
        return False
    hasExistingDisplay = False
    wokData = Data.get("Wok")
    if wokData and wokData.contains(FileKey):
        hasExistingDisplay = True
        ItemList = Data.getStringList("Wok." + FileKey + ".Items")
    if EventUtils.isRightClick(Event, EventType):
        MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
        ToolMaterials = ToolUtils.getToolMaterials(Config, "Wok", "Spatula")
        isToolValid = False
        for material in ToolMaterials:
            if ToolUtils.isToolItem(MainHandItem, Config, "Wok", "Spatula", material):
                isToolValid = True
                break
        if not isToolValid: 
            return False
        if hasExistingDisplay:
            TotalCount = Data.getInt("Wok." + FileKey + ".Count", 0)
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokTop"))
            for Item in ItemList:
                Parts = Item.split(" ")
                if len(Parts) >= 4:
                    PluginName, ItemName, Amount, Count = Parts[0], Parts[1], Parts[2], Parts[3]
                    ItemStack = ToolUtils.createItemStack(" ".join(Parts[0:2]))
                    if ItemStack:
                        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokContent"),
                            {"ItemName": ToolUtils.getItemDisplayName(ItemStack), "ItemAmount": Amount, "Count": Count})
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokDown"), {"Count": TotalCount})
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokHeatControl"), {"Heat": HeatLevel})
            EventUtils.setCancelled(Event, EventType, True)
            return True
        else:
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
            EventUtils.setCancelled(Event, EventType, True)
            return True
    elif EventUtils.isLeftClick(Event, EventType):
        if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.wok.stirfry"):
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
            EventUtils.setCancelled(Event, EventType, True)
            return False
        MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
        if MainHandItem and MainHandItem.getType() != Material.AIR:
            toolMaterials = ToolUtils.getToolMaterials(Config, "Wok", "Spatula")
            isToolValid = False
            for material in toolMaterials:
                if ToolUtils.isToolItem(MainHandItem, Config, "Wok", "Spatula", material):
                    isToolValid = True
                    break
            if isToolValid:
                if not hasExistingDisplay or not ItemList:
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                LastStirTime = Data.getLong("Wok." + FileKey + ".LastStirTime", 0)
                StirCount = Data.getInt("Wok." + FileKey + ".Count", 0)
                CurrentTime = System.currentTimeMillis()
                if StirCount != 0 and CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                StirFriedTime = Data.getLong("Wok." + FileKey + ".StirFriedTime", 0)
                if StirFriedTime != 0 and CurrentTime - StirFriedTime < Config.getInt("Setting.Wok.Delay") * 1000:
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.StirFriedTooQuickly"))
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                ParticleLocation = ClickBlock.getLocation().add(0.5, 1.1, 0.5)
                EventUtils.sendParticle("WokStirItem", ParticleLocation)
                Data.set("Wok." + FileKey + ".StirFriedTime", System.currentTimeMillis())
                Data.set("Wok." + FileKey + ".LastStirTime", System.currentTimeMillis())
                StirCount += 1
                if MainHandItem.getDurability() < MainHandItem.getType().getMaxDurability():
                    MainHandItem.setDurability(MainHandItem.getDurability() + 1)
                    ClickPlayer.getInventory().setItemInMainHand(MainHandItem)
                Data.set("Wok." + FileKey + ".Count", StirCount)
                UpdatedItemList = []
                for ItemEntry in ItemList:
                    Parts = ItemEntry.split(" ")
                    if len(Parts) >= 4:
                        ItemType = Parts[0]
                        ItemID = Parts[1]
                        Quantity = int(Parts[2])
                        StirTimes = int(Parts[3]) + 1
                        UpdatedEntry = "{} {} {} {}".format(ItemType, ItemID, Quantity, StirTimes)
                        UpdatedItemList.append(UpdatedEntry)
                
                Data.set("Wok." + FileKey + ".Items", UpdatedItemList)
                Data.save()
                MiniMessageUtils.sendActionBar(
                    ClickPlayer, Config.getString("Messages.ActionBar.StirCount"), {"Count": StirCount})
                MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokStirItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return True
        NeedBowl = Config.getBoolean("Setting.Wok.NeedBowl")
        if NeedBowl and MainHandItem and MainHandItem.getType() == Material.BOWL:
            if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.wok.serveout"):
                MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                EventUtils.setCancelled(Event, EventType, True)
                return False
            GetWokOutput(Data, FileKey, ClickPlayer, ClickBlock, HeatLevel)
            EventUtils.setCancelled(Event, EventType, True)
            return True
        if MainHandItem and MainHandItem.getType() != Material.AIR:
            CurrentItemIdentifier = ToolUtils.getItemIdentifier(MainHandItem)
            if hasExistingDisplay:
                NeedAddItem = False
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", MainHandItem)
                NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                for Index, ItemEntry in enumerate(ItemList):
                    Parts = ItemEntry.split(" ")
                    if len(Parts) >= 2:
                        ItemTypeID = Parts[0] + " " + Parts[1]
                        if ItemTypeID == CurrentItemIdentifier:
                            CurrentAmount = int(Parts[2]) + 1
                            StirCount = int(Parts[3])
                            ItemList[Index] = ItemTypeID + " " + str(CurrentAmount) + " " + str(StirCount)
                            NeedAddItem = True
                            for Display in NearbyDisplays:
                                if Display and not Display.isDead():
                                    DisplayItem = Display.getItemStack()
                                    if DisplayItem and ToolUtils.getItemIdentifier(DisplayItem) == CurrentItemIdentifier:
                                        DisplayItem.setAmount(CurrentAmount)
                                        Display.setItemStack(DisplayItem)
                                        break
                            break
                if not NeedAddItem:
                    ItemListLength = len(ItemList)
                    ExtraOffset = 0.0001 * ItemListLength
                    ItemList.append(CurrentItemIdentifier + " 1 0")
                    DisplayItem = MainHandItem.clone()
                    DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", MainHandItem, ExtraOffset)
                    CreateItemDisplay(DisplayLocation, DisplayItem, "Wok")
                Data.set("Wok." + FileKey + ".Items", list(ItemList))
                Data.save()
            else:
                if not BottomBlockType in HeatControl:
                    return False
                SaveValue = CurrentItemIdentifier + " 1 0"
                Data.set("Wok." + FileKey + ".Items", [SaveValue])
                Data.set("Wok." + FileKey + ".Count", 0)
                Data.save()
                DisplayItem = MainHandItem.clone()
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", MainHandItem)
                CreateItemDisplay(DisplayLocation, DisplayItem, "Wok")
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokAddItem"),
                {"Material": ToolUtils.getItemDisplayName(MainHandItem)})
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokAddItem"))
            EventUtils.setCancelled(Event, EventType, True)
            return True
        else:
            StirCount = Data.getInt("Wok." + FileKey + ".Count", 0)
            if StirCount > 0 and Config.getBoolean("Setting.Wok.Damage.Enable"):
                DamageValue = Config.getInt("Setting.Wok.Damage.Value")
                ClickPlayer.damage(DamageValue)
                MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokScald"))
                MiniMessageUtils.sendTitle(
                    ClickPlayer, Config.getString("Messages.Title.Scald.MainTitle"),
                    Config.getString("Messages.Title.Scald.SubTitle"), {"Damage": str(DamageValue)})
            if not hasExistingDisplay or not ItemList:
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return True
            LastItemEntry = ItemList[-1]
            Parts = LastItemEntry.split(" ")
            if len(Parts) < 4:
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return True
            ItemType = Parts[0]
            ItemID = Parts[1]
            Quantity = int(Parts[2])
            StirTimes = int(Parts[3])
            ItemToGive = ToolUtils.createItemStack(" ".join([ItemType, ItemID]))
            if ItemToGive:
                GiveItemToPlayer(ClickPlayer, ItemToGive)
            Quantity -= 1
            if Quantity <= 0:
                ItemList.pop()
                if not ItemList:
                    Data.set("Wok." + FileKey, None)
                else:
                    Data.set("Wok." + FileKey + ".Items", ItemList)
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", ItemToGive)
                NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                if NearbyDisplays:
                    TargetIdentifier = ToolUtils.getItemIdentifier(ItemToGive)
                    for display in NearbyDisplays:
                        if display and not display.isDead():
                            displayItem = display.getItemStack()
                            if displayItem and ToolUtils.getItemIdentifier(displayItem) == TargetIdentifier:
                                display.remove()
                                break
            else:
                ItemList[-1] = "{} {} {} {}".format(ItemType, ItemID, Quantity, StirTimes)
                Data.set("Wok." + FileKey + ".Items", ItemList)
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", ItemToGive)
                NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                if NearbyDisplays:
                    TargetIdentifier = ToolUtils.getItemIdentifier(ItemToGive)
                    for display in NearbyDisplays:
                        if display and not display.isDead():
                            displayItem = display.getItemStack()
                            if displayItem and ToolUtils.getItemIdentifier(displayItem) == TargetIdentifier:
                                displayItem.setAmount(Quantity)
                                display.setItemStack(displayItem)
                                break
            Data.save()
            EventUtils.setCancelled(Event, EventType, True)
            return True
    return False

def GetWokOutput(DataFile, FileKey, ClickPlayer, ClickBlock, HeatLevel=0):
    """
    获取炒锅的输出

    参数:
        DataFile: 数据文件对象
        Config: 配置文件对象
        FileKey: 炒锅的坐标和世界名
        ClickPlayer: 点击的玩家
        ClickBlock: 点击的方块
        HeatLevel: 热源等级 (默认为0)
    """
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    DataStirFryAmount = DataFile.getInt("Wok." + FileKey + ".Count")
    if DataStirFryAmount == 0:
        return
    ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
    if not ItemList:
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
        return
    RecipeKeys = WokRecipe.getKeys(False)
    for RecipeKey in RecipeKeys:
        RecipePermission = WokRecipe.getString(RecipeKey + ".Permission")
        if RecipePermission and not EventUtils.getPermission(ClickPlayer, RecipePermission):
            continue
        RecipeHeat = WokRecipe.getInt(RecipeKey + ".HeatControl", 0)
        if RecipeHeat != int(HeatLevel) and int(HeatLevel) != 0: continue
        RecipeItemList = WokRecipe.getStringList(RecipeKey + ".Item")
        if len(ItemList) != len(RecipeItemList): continue
        Match = True
        GreaterThan = 0
        LessThan = 0
        Tolerance = WokRecipe.getInt(RecipeKey + ".FaultTolerance", 0)
        Amount = 0
        for Idx in range(len(ItemList)):
            ItemEntry = ItemList[Idx].split(" ")
            RecipeEntry = RecipeItemList[Idx].split(" ")
            if len(ItemEntry) >= 2 and len(RecipeEntry) >= 2:
                if ItemEntry[0] != RecipeEntry[0] or ItemEntry[1] != RecipeEntry[1]:
                    Match = False
                    break
            else:
                if ItemList[Idx] != RecipeItemList[Idx]:
                    Match = False
                    break
            RecipeStirFry = RecipeEntry[3]
            ItemStirFry = int(ItemEntry[3])
            if "-" in RecipeStirFry:
                MinValue, MaxValue = map(int, RecipeStirFry.split("-"))
                if ItemStirFry < MinValue:
                    LessThan += 1
                    Amount += 1
                elif ItemStirFry > MaxValue:
                    GreaterThan += 1
                    Amount += 1
            else:
                RequiredStirFry = int(RecipeStirFry)
                if ItemStirFry < RequiredStirFry:
                    LessThan += 1
                    Amount += 1
                elif ItemStirFry > RequiredStirFry:
                    GreaterThan += 1
                    Amount += 1
            if Amount > Tolerance:
                Match = False
                break
        if Match:
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            StirFryAmount = WokRecipe.get(RecipeKey + ".Count")
            if "-" in StirFryAmount:
                minValue, maxValue = map(int, StirFryAmount.split("-"))
                MaxValue = max(minValue, maxValue)
                MinValue = min(minValue, maxValue)
            else:
                MaxValue = WokRecipe.getInt(RecipeKey + ".Count")
                MinValue = WokRecipe.getInt(RecipeKey + ".Count")
            LastStirTime = DataFile.getLong("Wok." + FileKey + ".LastStirTime", 0)
            CurrentTime = System.currentTimeMillis()
            if CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                RawItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                return
            if DataStirFryAmount > MaxValue:
                BurntItem = WokRecipe.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, BurntItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.RawFood"))
                return
            elif DataStirFryAmount < MinValue:
                RawItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                return
            if Config.getBoolean("Setting.Wok.Failure.Enable"):
                Chance = Config.getInt("Setting.Wok.Failure.Chance")
                if random.randint(1, 100) < Chance:
                    ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
                    OutputWokItem(RecipeKey, ErrorRecipe, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.FailureRecipe"))
                    return
            if Amount <= Tolerance:
                OutputWokItem(RecipeKey, RecipeKey, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.SuccessRecipe"))
                return
            elif GreaterThan > LessThan:
                BurntItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, BurntItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                return
            elif LessThan > GreaterThan:
                RawItem = WokRecipe.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.RawFood"))
                return
    if Config.getBoolean("Setting.Wok.Failure.Enable"):
        RemoveItemToPlayer(ClickPlayer, MainHandItem)
        ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
        OutputWokItem(RecipeKey, ErrorRecipe, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.ErrorRecipe"))
        return

def OutputWokItem(RecipeKey, Item, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock):
    """输出炒锅物品，并清除展示实体与数据

    参数
        RecipeKey: 配方Key
        Item: 输出物品标识符
        RecipeConfig: 配方配置文件
        ClickPlayer: 点击玩家
        DataFile: 玩家数据文件
        FileKey: 玩家数据文件Key
        ClickBlock: 点击方块
    """
    GiveAmount = RecipeConfig.getInt(RecipeKey + ".Amount", 1)
    ITEM = ToolUtils.createItemStack(RecipeKey, GiveAmount)
    if ITEM is None:
        ITEM = ToolUtils.createItemStack(Item, GiveAmount)
        if ITEM is None:
            return
    if Config.getBoolean("Setting.Wok.Drop"):
        DropLocation = ClickBlock.getLocation().add(0.5, 1.0, 0.5)
        ItemEntity = ClickBlock.getWorld().dropItem(DropLocation, ITEM)
        ItemEntity.setPickupDelay(20)
    else:
        GiveItemToPlayer(ClickPlayer, ITEM)
    DataFile.set("Wok." + FileKey, None)
    DataFile.save()
    DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok")
    NearbyDisplays = FindNearbyDisplay(DisplayLocation)
    if NearbyDisplays:
        for display in NearbyDisplays:
            if display and not display.isDead():display.remove()

GrinderTask = None

def GrinderInteraction(Event, EventType):
    """处理研磨机交互事件"""
    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    if not ClickBlock or not MainHandItem or MainHandItem.getType() == Material.AIR: return False
    if not EventUtils.isLeftClick(Event, EventType) or not EventUtils.isSneaking(ClickPlayer, "Grinder"): return False
    if not EventUtils.isTargetBlock(ClickBlock, "Grinder"): return False
    FileKey = GetFileKey(ClickBlock)
    if Data.contains("Grinder." + FileKey):
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.OnRunGrinder"))
        EventUtils.setCancelled(Event, EventType, True)
        return True
    ItemIdentifier = ToolUtils.getItemIdentifier(MainHandItem)
    RecipeKeys = GrinderRecipe.getKeys(False)
    if ItemIdentifier not in RecipeKeys:
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.NoGrinderReplace"))
        EventUtils.setCancelled(Event, EventType, True)
        return False
    RecipePermission = GrinderRecipe.getString(ItemIdentifier + ".Permission")
    if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.grinder.interaction"):
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        EventUtils.setCancelled(Event, EventType, True)
        return False
    if RecipePermission and not EventUtils.getPermission(ClickPlayer, RecipePermission):
        EventUtils.setCancelled(Event, EventType, True)
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        return False
    RemoveItemToPlayer(ClickPlayer, MainHandItem)
    GrindTime = GrinderRecipe.getInt(ItemIdentifier + ".GrindingTime", 5)
    CurrentTime = System.currentTimeMillis()
    Data.set("Grinder." + FileKey + ".StartTime", CurrentTime)
    Data.set("Grinder." + FileKey + ".Input", ItemIdentifier)
    Data.set("Grinder." + FileKey + ".Player", ClickPlayer.getName())
    Data.save()
    MainTitle = Config.getString("Messages.Title.Grinder.MainTitle")
    SubTitle = Config.getString("Messages.Title.Grinder.SubTitle")
    MiniMessageUtils.sendTitle(ClickPlayer, MainTitle, SubTitle, {"Time": GrindTime})
    StartGrinderCheckTask()
    EventUtils.setCancelled(Event, EventType, True)
    return True

def StartGrinderCheckTask():
    """启动或重启研磨检查任务"""
    global GrinderTask
    if GrinderTask is not None:
        try:
            ps.scheduler.stopTask(GrinderTask)
        except:
            pass
        GrinderTask = None
    grinderSection = Data.getConfigurationSection("Grinder")
    if grinderSection is None:
        return
    grinderKeys = grinderSection.getKeys(False)
    if not grinderKeys:
        return
    CheckDelay = Config.getInt("Setting.Grinder.CheckDelay", 20)
    GrinderTask = ps.scheduler.scheduleRepeatingTask(CheckAllGrinders, CheckDelay, CheckDelay)

def CheckAllGrinders():
    """检查所有研磨机的完成状态"""
    global GrinderTask
    grinderSection = Data.getConfigurationSection("Grinder")
    if grinderSection is None:
        if GrinderTask is not None:
            try:
                ps.scheduler.stopTask(GrinderTask)
            except:
                pass
            GrinderTask = None
        return
    grinderKeys = grinderSection.getKeys(False)
    if not grinderKeys:
        if GrinderTask is not None:
            try:
                ps.scheduler.stopTask(GrinderTask)
            except:
                GrinderTask = None
        return
    for grinderKey in grinderKeys:
        CheckSingleGrinder(grinderKey)

def CheckSingleGrinder(FileKey):
    """检查单个研磨机的完成状态"""
    if not Data.contains("Grinder." + FileKey):
        return
    InputItem = Data.getString("Grinder." + FileKey + ".Input")
    if not InputItem:
        Data.set("Grinder." + FileKey, None)
        Data.save()
        return
    GrindTime = GrinderRecipe.getInt(InputItem + ".GrindingTime", 5)
    OutputItems = GrinderRecipe.getStringList(InputItem + ".Output")
    StartTime = Data.getLong("Grinder." + FileKey + ".StartTime")
    CurrentTime = System.currentTimeMillis()
    Parts = FileKey.split(",")
    BlockX = int(Parts[0])
    BlockY = int(Parts[1])
    BlockZ = int(Parts[2])
    WorldName = Parts[3]
    World = Bukkit.getWorld(WorldName)
    BlockLocation = Location(World, BlockX, BlockY, BlockZ)
    PlayerName = Data.getString("Grinder." + FileKey + ".Player")
    Player = Bukkit.getPlayer(PlayerName)
    if CurrentTime - StartTime >= GrindTime * 1000:
        if len(Parts) < 4:
            Data.set("Grinder." + FileKey, None)
            Data.save()
            return
        if World is None:
            Data.set("Grinder." + FileKey, None)
            Data.save()
            return
        for OutputItem in OutputItems:
            if ToolUtils.processReward(OutputItem, Player):
                continue
        Data.set("Grinder." + FileKey, None)
        Data.save()
    else:
        EventUtils.sendParticle("GrinderStart", BlockLocation.add(0.5, 1.0, 0.5))
        SoundName = Config.getString("Setting.Sound.GrinderStart")
        SoundLocation = BlockLocation.add(0.5, 0.5, 0.5)
        MiniMessageUtils.playSound(SoundLocation, SoundName)

CheckAllGrinders()

SteamerTempData = {}
SteamerInventories = {}
SteamerTask = None
SteamerProcessingData = {}

def SteamerInteraction(Event, EventType):
    """蒸锅交互事件处理"""
    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    if not ClickBlock:  return False
    if EventUtils.isTargetBlock(ClickBlock, "Steamer"):
        if not EventUtils.isMainHand(Event, EventType):  return False
        if not EventUtils.isRightClick(Event, EventType):  return False
        if not EventUtils.isSneaking(ClickPlayer, "Steamer"):    return False
        BottomBlock = ClickBlock.getRelative(BlockFace.DOWN)
        if not isHeatSourceBlock(BottomBlock):
            return False
        if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.steamer.interaction"):
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
            EventUtils.setCancelled(Event, EventType, True)
            return True
        EventUtils.setCancelled(Event, EventType, True)
        OpenSteamerGUI(ClickPlayer, ClickBlock)
        return True
    
    # 检查热源方块交互
    elif isHeatSourceBlock(ClickBlock):
        TopBlock = ClickBlock.getRelative(BlockFace.UP)
        if not EventUtils.isTargetBlock(TopBlock, "Steamer"): return False
        MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
        if (not MainHandItem or MainHandItem.getType() == Material.AIR) and EventUtils.isRightClick(Event, EventType):
            if not EventUtils.isSneaking(ClickPlayer, "Steamer"):  return False
            EventUtils.setCancelled(Event, EventType, True)
            SteamerFileKey = GetFileKey(TopBlock)
            return ShowSteamerInfo(ClickPlayer, SteamerFileKey)
        if not EventUtils.isMainHand(Event, EventType):  return False
        if not EventUtils.isRightClick(Event, EventType):  return False
        if not EventUtils.isSneaking(ClickPlayer, "Steamer"):  return False
        if not MainHandItem or MainHandItem.getType() == Material.AIR:
            EventUtils.setCancelled(Event, EventType, True)
            return True
        ItemIdentifier = ToolUtils.getItemIdentifier(MainHandItem)
        IsMoistureItem = False
        MoistureValue = 0
        OutputItem = None
        MoistureConfig = Config.getStringList("Setting.Steamer.Moisture")
        for moistureEntry in MoistureConfig:
            try:
                parts = moistureEntry.split(" & ")
                if len(parts) >= 3:
                    inputItem = parts[0].strip()
                    outputItem = parts[1].strip() if len(parts) > 1 else "AIR"
                    moistureVal = int(parts[2].strip()) if len(parts) > 2 else 0
                    if inputItem == ItemIdentifier:
                        IsMoistureItem = True
                        MoistureValue = moistureVal
                        OutputItem = outputItem if outputItem != "AIR" else None
                        break
                    ItemParts = ItemIdentifier.split(" ")
                    if len(ItemParts) >= 2:
                        ItemNamespace = ItemParts[0]
                        ItemID = ItemParts[1]
                        configParts = inputItem.split(" ")
                        if len(configParts) >= 2:
                            configNamespace = configParts[0]
                            configID = configParts[1]
                            if configID == ItemID:
                                IsMoistureItem = True
                                MoistureValue = moistureVal
                                OutputItem = outputItem if outputItem != "AIR" else None
                                break
                        else:
                            if inputItem == ItemID:
                                IsMoistureItem = True
                                MoistureValue = moistureVal
                                OutputItem = outputItem if outputItem != "AIR" else None
                                break
            except Exception as e:
                continue
        if IsMoistureItem:
            if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.steamer.addmoisture"):
                MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                EventUtils.setCancelled(Event, EventType, True)
                return True
            EventUtils.setCancelled(Event, EventType, True)
            SteamerFileKey = GetFileKey(TopBlock)
            return AddMoistureToSteamer(ClickPlayer, MainHandItem, MoistureValue, OutputItem, SteamerFileKey)
        IsValidFuel = False
        FuelDuration = 0
        FuelConfig = Config.get("Setting.Steamer.Fuel")
        if FuelConfig:
            FuelKeys = FuelConfig.getKeys(False)
            if ItemIdentifier in FuelKeys:
                IsValidFuel = True
                FuelDuration = FuelConfig.getInt(ItemIdentifier)
            else:
                ItemParts = ItemIdentifier.split(" ")
                if len(ItemParts) >= 2:
                    ItemIDOnly = ItemParts[1]
                    if ItemIDOnly in FuelKeys:
                        IsValidFuel = True
                        FuelDuration = FuelConfig.getInt(ItemIDOnly)
                    else:
                        for fuelKey in FuelKeys:
                            if ":" in fuelKey:
                                namespace, key_id = fuelKey.split(":", 1)
                                if key_id == ItemIDOnly:
                                    IsValidFuel = True
                                    FuelDuration = FuelConfig.getInt(fuelKey)
                                    break
                            else:
                                if fuelKey == ItemIDOnly:
                                    IsValidFuel = True
                                    FuelDuration = FuelConfig.getInt(fuelKey)
                                    break
        if IsValidFuel:
            if not EventUtils.getPermission(ClickPlayer, "jiuwukitchen.steamer.addfuel"):
                MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                EventUtils.setCancelled(Event, EventType, True)
                return True
            EventUtils.setCancelled(Event, EventType, True)
            SteamerFileKey = GetFileKey(TopBlock)
            return AddFuelToHeatSource(ClickPlayer, MainHandItem, FuelDuration, SteamerFileKey, ClickBlock)
        EventUtils.setCancelled(Event, EventType, True)
        return True
    return False

def ShowSteamerInfo(Player, SteamerFileKey):
    """显示蒸锅信息到ActionBar，包含烹饪进度状态
    
    参数:
        Player: 玩家对象
        SteamerFileKey: 蒸锅的数据键
        
    返回:
        bool: 是否成功显示信息
    """
    try:
        CoolingTimePath = "Steamer." + SteamerFileKey + ".CoolingTime"
        MoisturePath = "Steamer." + SteamerFileKey + ".Moisture"
        SteamPath = "Steamer." + SteamerFileKey + ".Steam"
        CurrentTime = System.currentTimeMillis()
        CoolingTime = Data.getLong(CoolingTimePath, 0)
        Moisture = Data.getInt(MoisturePath, 0)
        Steam = Data.getInt(SteamPath, 0)
        RemainingBurnTime = 0
        if CoolingTime > CurrentTime:
            RemainingBurnTime = (CoolingTime - CurrentTime) // 1000
        ProgressStatus = CalculateCookingProgress(SteamerFileKey)
        Placeholders = {
            "BurningTime": RemainingBurnTime, 
            "Moisture": Moisture, 
            "Steam": Steam,
            "Progress": ProgressStatus
        }
        MiniMessageUtils.sendActionBar(Player, Config.getString("Messages.ActionBar.SteamerInfo"), Placeholders)
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def CalculateCookingProgress(SteamerFileKey):
    """计算蒸锅的烹饪进度状态"""
    try:
        SlotsPath = "Steamer." + SteamerFileKey + ".Slots"
        CookingProgressPath = "Steamer." + SteamerFileKey + ".CookingProgress"
        SteamPath = "Steamer." + SteamerFileKey + ".Steam"
        CurrentSteam = Data.getInt(SteamPath, 0)
        if CurrentSteam <= 0:
            if not Data.contains(SlotsPath) or not Data.contains(CookingProgressPath):
                return Config.getString("Messages.NotStarted")
            Slots = Data.getStringList(SlotsPath)
            CookingProgress = Data.getIntegerList(CookingProgressPath)
            AllProgressZero = True
            for progress in CookingProgress:
                if progress > 0:
                    AllProgressZero = False
                    break
            if AllProgressZero:
                return Config.getString("Messages.NotStarted")
        if not Data.contains(SlotsPath) or not Data.contains(CookingProgressPath):
            return Config.getString("Messages.NotStarted")
        Slots = Data.getStringList(SlotsPath)
        CookingProgress = Data.getIntegerList(CookingProgressPath)
        if len(CookingProgress) < len(Slots):
            CookingProgress.extend([0] * (len(Slots) - len(CookingProgress)))
        elif len(CookingProgress) > len(Slots):
            CookingProgress = CookingProgress[:len(Slots)]
        TotalRequiredSteam = 0
        TotalCurrentProgress = 0
        HasValidIngredients = False
        AllItemsCompleted = True
        ActiveItemsCount = 0
        for i in range(len(Slots)):
            if i >= len(CookingProgress):
                continue
            itemIdentifier = Slots[i]
            if itemIdentifier == "AIR":
                continue
            isInputItem = SteamerRecipe.contains(itemIdentifier)
            isOutputItem = False
            originalInputItem = None
            if not isInputItem:
                for recipeKey in SteamerRecipe.getKeys(False):
                    outputItem = SteamerRecipe.getString(recipeKey + ".Output")
                    if outputItem and outputItem == itemIdentifier:
                        isOutputItem = True
                        originalInputItem = recipeKey
                        break
            if not isInputItem and not isOutputItem:
                AllItemsCompleted = False
                continue
            ActiveItemsCount += 1
            HasValidIngredients = True
            if isInputItem:
                currentItem = itemIdentifier
                RecipeSteam = SteamerRecipe.getInt(currentItem + ".Steam", 0)
            else:
                currentItem = originalInputItem
                RecipeSteam = SteamerRecipe.getInt(currentItem + ".Steam", 0)
            OutputItem = SteamerRecipe.getString(currentItem + ".Output")
            if RecipeSteam <= 0 or not OutputItem:
                AllItemsCompleted = False
                continue
            TotalRequiredSteam += RecipeSteam
            if i < len(CookingProgress):
                CurrentProgress = CookingProgress[i]
                if isOutputItem:
                    TotalCurrentProgress += RecipeSteam
                else:
                    TotalCurrentProgress += min(CurrentProgress, RecipeSteam)
                if isOutputItem or CurrentProgress >= RecipeSteam:
                    pass
                else:
                    AllItemsCompleted = False
            else:
                AllItemsCompleted = False
        if not HasValidIngredients or ActiveItemsCount == 0:
            return Config.getString("Messages.NotStarted")
        if AllItemsCompleted and ActiveItemsCount > 0:
            return Config.getString("Messages.Completed")
        if CurrentSteam <= 0 and TotalCurrentProgress == 0:
            return Config.getString("Messages.NotStarted")
        if TotalRequiredSteam > 0:
            Percentage = (float(TotalCurrentProgress) / TotalRequiredSteam) * 100
            Percentage = max(0, min(100, Percentage))
            FormattedPercentage = "{:.2f}%".format(Percentage)
            return FormattedPercentage
        else:
            return "0.00%"
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return Config.getString("Messages.NotStarted")

def isHeatSourceBlock(Block):
    """判断方块是否是有效的热源方块"""
    HeatControlList = Config.getStringList("Setting.Steamer.HeatControl")
    if not HeatControlList: return False
    if Block.getType().name() in HeatControlList: return True
    if CraftEngineAvailable:
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks  # type: ignore
            if CraftEngineBlocks.isCustomBlock(Block):
                BlockState = CraftEngineBlocks.getCustomBlockState(Block)
                CraftEngineKey = "craftengine " + str(BlockState)
                return CraftEngineKey in HeatControlList
        except:
            pass
    return False

def OpenSteamerGUI(Player, SteamerBlock):
    """打开蒸锅GUI"""
    try:
        InventoryTypeStr = Config.getString("Setting.Steamer.OpenInventory.Type", "HOPPER")
        TitleText = Config.getString("Setting.Steamer.OpenInventory.Title", u"<dark_gray>蒸锅")
        SlotCount = Config.getInt("Setting.Steamer.OpenInventory.Slot", 9)
        TargetInventoryType = None
        try:
            TargetInventoryType = InventoryType.valueOf(InventoryTypeStr)
        except:
            TargetInventoryType = InventoryType.HOPPER
        TitleComponent = MiniMessageUtils.processMessage(TitleText)
        if TargetInventoryType == InventoryType.CHEST:
            if SlotCount % 9 != 0:
                SlotCount = (SlotCount // 9) * 9
                if SlotCount < 9:
                    SlotCount = 9
            Inventory = Bukkit.createInventory(None, SlotCount, TitleComponent)
        else:
            Inventory = Bukkit.createInventory(None, TargetInventoryType, TitleComponent)
            SlotCount = Inventory.getSize()
        SteamerKey = GetFileKey(SteamerBlock)
        PlayerUUID = Player.getUniqueId().toString()
        SteamerTempData[PlayerUUID] = {
            "steamerKey": SteamerKey,
            "block": SteamerBlock,
            "inventoryType": InventoryTypeStr,
            "slotCount": SlotCount
        }
        SteamerInventories[PlayerUUID] = Inventory
        LoadSteamerInventory(SteamerKey, Inventory)
        Player.openInventory(Inventory)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def LoadSteamerInventory(SteamerKey, Inventory):
    """加载蒸锅已有的物品到GUI中，基于槽位索引独立加载进度"""
    try:
        SlotsPath = "Steamer." + SteamerKey + ".Slots"
        CookingProgressPath = "Steamer." + SteamerKey + ".CookingProgress"
        if Data.contains(SlotsPath):
            SlotItems = Data.getStringList(SlotsPath)
            CookingProgress = []
            if Data.contains(CookingProgressPath):
                CookingProgress = Data.getIntegerList(CookingProgressPath)
            else:
                CookingProgress = [0] * len(SlotItems)
            if len(CookingProgress) < len(SlotItems):
                CookingProgress.extend([0] * (len(SlotItems) - len(CookingProgress)))
            elif len(CookingProgress) > len(SlotItems):
                CookingProgress = CookingProgress[:len(SlotItems)]
            for i, itemIdentifier in enumerate(SlotItems):
                if i >= Inventory.getSize():
                    break
                if itemIdentifier != "AIR":
                    ItemStack = ToolUtils.createItemStack(itemIdentifier, 1)
                    if ItemStack:
                        Inventory.setItem(i, ItemStack)
            Data.set(CookingProgressPath, CookingProgress)
            Data.save()
        else:
            Data.set(CookingProgressPath, [])
            Data.save()
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def SteamerInventoryClose(Event):
    """蒸锅GUI关闭事件处理"""
    Player = Event.getPlayer()
    PlayerUUID = Player.getUniqueId().toString()
    if PlayerUUID not in SteamerTempData: 
        return
    Inventory = Event.getInventory()
    SteamerData = SteamerTempData[PlayerUUID]
    SteamerKey = SteamerData["steamerKey"]
    ProcessExcessSteamerItems(Player, Inventory)
    SaveSteamerInventory(SteamerKey, Inventory)
    if PlayerUUID in SteamerTempData:
        del SteamerTempData[PlayerUUID]
    if PlayerUUID in SteamerInventories:
        del SteamerInventories[PlayerUUID]
    slotsPath = "Steamer." + SteamerKey + ".Slots"
    if Data.contains(slotsPath):
        slots = Data.getStringList(slotsPath)
        hasValidIngredients = False
        for itemIdentifier in slots:
            if itemIdentifier != "AIR" and SteamerRecipe.contains(itemIdentifier):
                hasValidIngredients = True
                break
        if hasValidIngredients:
            StartSteamerTimer()

ps.listener.registerListener(SteamerInventoryClose, InventoryCloseEvent)

def ProcessExcessSteamerItems(Player, Inventory):
    """处理蒸锅GUI中的多余物品
    
    参数:
        Player: 玩家对象
        Inventory: 库存对象
    """
    try:
        for slot in range(Inventory.getSize()):
            item = Inventory.getItem(slot)
            if item and item.getType() != Material.AIR and item.getAmount() > 1:
                excess_amount = item.getAmount() - 1
                excess_item = item.clone()
                excess_item.setAmount(excess_amount)
                item.setAmount(1)
                Inventory.setItem(slot, item)
                ReturnExcessItemsToPlayer(Player, excess_item)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def ReturnExcessItemsToPlayer(Player, ExcessItem):
    """将多余物品返还给玩家
    
    参数:
        Player: 玩家对象
        ExcessItem: 多余的物品
    """
    try:
        if Player.getInventory().firstEmpty() != -1:
            Player.getInventory().addItem(ExcessItem)
        else:
            drop_location = Player.getLocation()
            Player.getWorld().dropItemNaturally(drop_location, ExcessItem)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def SaveSteamerInventory(SteamerKey, Inventory):
    """保存蒸锅GUI中的物品数据和烹饪进度"""
    try:
        OldSlotsPath = "Steamer." + SteamerKey + ".Slots"
        OldCookingProgressPath = "Steamer." + SteamerKey + ".CookingProgress"
        
        OldSlots = []
        OldCookingProgress = []
        if Data.contains(OldSlotsPath):
            OldSlots = Data.getStringList(OldSlotsPath)
        if Data.contains(OldCookingProgressPath):
            OldCookingProgress = Data.getIntegerList(OldCookingProgressPath)
        NewSlotItems = []
        NewCookingProgress = []
        for i in range(Inventory.getSize()):
            Item = Inventory.getItem(i)
            if Item and Item.getType() != Material.AIR:
                ItemIdentifier = ToolUtils.getItemIdentifier(Item)
                NewSlotItems.append(ItemIdentifier)
                if i < len(OldCookingProgress) and i < len(OldSlots) and OldSlots[i] == ItemIdentifier:
                    NewCookingProgress.append(OldCookingProgress[i])
                else:
                    NewCookingProgress.append(0)
            else:
                NewSlotItems.append("AIR")
                NewCookingProgress.append(0)
        Data.set(OldSlotsPath, NewSlotItems)
        Data.set(OldCookingProgressPath, NewCookingProgress)
        Data.save()
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def AddFuelToHeatSource(Player, FuelItem, FuelDuration, SteamerFileKey, HeatSourceBlock):
    """向热源方块添加燃料"""
    try:
        CurrentTime = System.currentTimeMillis()
        FuelDurationMs = FuelDuration * 1000
        CoolingTimePath = "Steamer." + SteamerFileKey + ".CoolingTime"
        CurrentCoolingTime = Data.getLong(CoolingTimePath, 0)
        if CurrentCoolingTime > CurrentTime:
            NewCoolingTime = CurrentCoolingTime + FuelDurationMs
        else:
            NewCoolingTime = CurrentTime + FuelDurationMs
        Data.set(CoolingTimePath, NewCoolingTime)
        Data.save()
        RemoveItemToPlayer(Player, FuelItem)
        RemainingSeconds = (NewCoolingTime - CurrentTime) // 1000
        IgniteHeatSourceBlock(HeatSourceBlock, RemainingSeconds)
        StartSteamerTimer()
        FuelName = ToolUtils.getItemDisplayName(FuelItem)
        MiniMessageUtils.sendActionBar(Player, Config.getString("Messages.ActionBar.AddFuel"),
            {"Item": FuelName, "Second": str(RemainingSeconds)})
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def AddMoistureToSteamer(Player, MoistureItem, MoistureValue, OutputItem, SteamerFileKey):
    """向蒸锅添加水份"""
    try:
        MoisturePath = "Steamer." + SteamerFileKey + ".Moisture"
        CurrentMoisture = Data.getInt(MoisturePath, 0)
        NewMoisture = CurrentMoisture + MoistureValue
        Data.set(MoisturePath, NewMoisture)
        Data.save()
        RemoveItemToPlayer(Player, MoistureItem)
        if OutputItem and OutputItem != "AIR":
            OutputItemStack = ToolUtils.createItemStack(OutputItem, 1)
            if OutputItemStack:
                GiveItemToPlayer(Player, OutputItemStack)
        if NewMoisture > 0:
            StartSteamerTimer()
        ItemName = ToolUtils.getItemDisplayName(MoistureItem)
        MiniMessageUtils.sendActionBar(Player, Config.getString("Messages.ActionBar.AddMoisture"),
            {"Item": ItemName, "Moisture": str(MoistureValue), "Total": str(NewMoisture)})
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def IgniteHeatSourceBlock(HeatSourceBlock, RemainingSeconds):
    """点燃热源方块"""
    try:
        blockType = HeatSourceBlock.getType()
        if blockType == Material.CAMPFIRE or blockType == Material.SOUL_CAMPFIRE:
            blockData = HeatSourceBlock.getBlockData()
            if hasattr(blockData, 'setLit'):
                blockData.setLit(True)
                HeatSourceBlock.setBlockData(blockData)
        elif blockType in [Material.FURNACE, Material.BLAST_FURNACE, Material.SMOKER]:
            furnaceState = HeatSourceBlock.getState()
            if hasattr(furnaceState, 'setBurnTime'):
                furnaceState.setBurnTime(RemainingSeconds * 20)
                furnaceState.update()
        HeatSourceBlock.getState().update()
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def StartSteamerTimer():
    """启动蒸锅全局计时器"""
    global SteamerTask
    if SteamerTask is not None:
        try:
            ps.scheduler.stopTask(SteamerTask)
        except:
            pass
    SteamerTask = ps.scheduler.scheduleRepeatingTask(ProcessAllSteamers, 20, 20)

def ProcessAllSteamers():
    """处理所有蒸锅的蒸汽产生和消耗"""
    global SteamerTask
    try:
        steamerSection = Data.getConfigurationSection("Steamer")
        if steamerSection is None:
            if SteamerTask is not None:
                try:
                    ps.scheduler.stopTask(SteamerTask)
                    SteamerTask = None
                except:
                    pass
            return
        steamerKeys = steamerSection.getKeys(False)
        if not steamerKeys:
            if SteamerTask is not None:
                try:
                    ps.scheduler.stopTask(SteamerTask)
                    SteamerTask = None
                except:
                    pass
            return
        currentTime = System.currentTimeMillis()
        hasActiveSteamer = False
        for steamerKey in steamerKeys:
            coolingTimePath = "Steamer." + steamerKey + ".CoolingTime"
            coolingTime = Data.getLong(coolingTimePath, 0)
            if coolingTime > 0 and currentTime >= coolingTime:
                ExtinguishHeatSource(steamerKey)
                Data.set(coolingTimePath, 0)
                Data.save()
            if coolingTime > currentTime:
                if ProcessSteamProduction(steamerKey):
                    hasActiveSteamer = True
            if ProcessSteamConsumptionAndCooking(steamerKey):
                hasActiveSteamer = True
        if not hasActiveSteamer and SteamerTask is not None:
            try:
                ps.scheduler.stopTask(SteamerTask)
                SteamerTask = None
            except:
                pass
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def ProcessSingleSteamer(steamerKey, currentTime):
    """处理单个蒸锅的蒸汽逻辑和食材烹饪"""
    try:
        coolingTimePath = "Steamer." + steamerKey + ".CoolingTime"
        coolingTime = Data.getLong(coolingTimePath, 0)
        shouldExtinguish = False
        if coolingTime > 0 and currentTime >= coolingTime:
            ExtinguishHeatSource(steamerKey)
            Data.set(coolingTimePath, 0)
            Data.save()
            shouldExtinguish = True
        isActive = False
        if coolingTime > currentTime:
            if ProcessSteamProduction(steamerKey):
                isActive = True
        if ProcessSteamConsumptionAndCooking(steamerKey):
            isActive = True
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentSteam = Data.getInt(steamPath, 0)
        if shouldExtinguish and currentSteam > 0:
            isActive = True
        return isActive
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ProcessSteamConsumptionAndCooking(steamerKey):
    """处理蒸汽消耗和食材烹饪"""
    try:
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentSteam = Data.getInt(steamPath, 0)
        resetToZero = Config.getBoolean("Setting.Steamer.ResetToZero", True)
        if currentSteam <= 0 and resetToZero:
            return False
        steamConversionEfficiency = Config.getInt("Setting.Steamer.SteamConversionEfficiency", 1)
        steamConsumptionEfficiency = Config.getInt("Setting.Steamer.SteamConsumptionEfficiency", 1)
        slotsPath = "Steamer." + steamerKey + ".Slots"
        cookingProgressPath = "Steamer." + steamerKey + ".CookingProgress"
        if not Data.contains(slotsPath):
            newSteam = max(0, currentSteam - steamConsumptionEfficiency)
            Data.set(steamPath, newSteam)
            Data.save()
            return newSteam > 0
        slots = Data.getStringList(slotsPath)
        cookingProgress = []
        if Data.contains(cookingProgressPath):
            cookingProgress = Data.getIntegerList(cookingProgressPath)
        else:
            cookingProgress = [0] * len(slots)
            Data.set(cookingProgressPath, cookingProgress)
            Data.save()
        if len(cookingProgress) < len(slots):
            cookingProgress.extend([0] * (len(slots) - len(cookingProgress)))
        elif len(cookingProgress) > len(slots):
            cookingProgress = cookingProgress[:len(slots)]
        validIngredients = 0
        totalIngredientConsumption = 0
        for i, itemIdentifier in enumerate(slots):
            if itemIdentifier != "AIR" and SteamerRecipe.contains(itemIdentifier):
                validIngredients += 1
                totalIngredientConsumption += steamConversionEfficiency
        totalSteamConsumption = steamConsumptionEfficiency + totalIngredientConsumption
        if currentSteam < totalSteamConsumption:
            availableForIngredients = max(0, currentSteam - steamConsumptionEfficiency)
            if availableForIngredients <= 0:
                newSteam = 0
                Data.set(steamPath, newSteam)
                Data.save()
                return False
            actualIngredientConsumption = min(availableForIngredients, totalIngredientConsumption)
            newSteam = max(0, currentSteam - steamConsumptionEfficiency - actualIngredientConsumption)
            if totalIngredientConsumption > 0:
                progressRatio = float(actualIngredientConsumption) / float(totalIngredientConsumption)
                for i, itemIdentifier in enumerate(slots):
                    if i >= len(cookingProgress):
                        continue
                    if itemIdentifier != "AIR" and SteamerRecipe.contains(itemIdentifier):
                        additionalProgress = int(steamConversionEfficiency * progressRatio)
                        cookingProgress[i] = min(cookingProgress[i] + additionalProgress, 
                                              SteamerRecipe.getInt(itemIdentifier + ".Steam", 0))
            Data.set(steamPath, newSteam)
            Data.set(cookingProgressPath, cookingProgress)
            Data.save()
            return newSteam > 0
        newSteam = currentSteam - totalSteamConsumption
        Data.set(steamPath, newSteam)
        completedItems = []
        for i in range(len(slots)):
            if i >= len(cookingProgress):
                continue
            itemIdentifier = slots[i]
            if itemIdentifier == "AIR" or not SteamerRecipe.contains(itemIdentifier):
                continue
            recipeSteam = SteamerRecipe.getInt(itemIdentifier + ".Steam", 0)
            outputItem = SteamerRecipe.getString(itemIdentifier + ".Output")
            if recipeSteam <= 0 or not outputItem:
                continue
            currentProgress = cookingProgress[i]
            newProgress = currentProgress + steamConversionEfficiency
            cookingProgress[i] = newProgress
            if newProgress >= recipeSteam:
                slots[i] = outputItem
                cookingProgress[i] = 0
                completedItems.append((i, outputItem))
        Data.set(slotsPath, slots)
        Data.set(cookingProgressPath, cookingProgress)
        Data.save()
        return validIngredients > 0 or newSteam > 0
        
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ExtinguishHeatSource(SteamerFileKey):
    """通过蒸锅熄灭热源方块"""
    try:
        parts = SteamerFileKey.split(",")
        if len(parts) < 4:
            return False
        x = int(parts[0])
        y = int(parts[1])
        z = int(parts[2])
        worldName = parts[3]
        world = Bukkit.getWorld(worldName)
        if not world:
            return False
        steamerLocation = Location(world, x, y, z)
        heatSourceBlock = steamerLocation.getBlock().getRelative(BlockFace.DOWN)
        if not isHeatSourceBlock(heatSourceBlock):
            return False
        if heatSourceBlock.getType() in [Material.CAMPFIRE, Material.SOUL_CAMPFIRE]:
            blockData = heatSourceBlock.getBlockData()
            if hasattr(blockData, 'setLit'):
                blockData.setLit(False)
                heatSourceBlock.setBlockData(blockData)
        elif heatSourceBlock.getType() in [Material.FURNACE, Material.BLAST_FURNACE, Material.SMOKER]:
            furnaceState = heatSourceBlock.getState()
            if hasattr(furnaceState, 'setBurnTime'):
                furnaceState.setBurnTime(0)
                furnaceState.update()
        heatSourceBlock.getState().update()
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ProcessSteamProduction(steamerKey):
    """处理蒸汽产生"""
    try:
        moisturePath = "Steamer." + steamerKey + ".Moisture"
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentMoisture = Data.getInt(moisturePath, 0)
        currentSteam = Data.getInt(steamPath, 0)
        if currentMoisture <= 0:
            return False
        productionEfficiency = Config.getInt("Setting.Steamer.SteamProductionEfficiency", 10)
        steamProduced = min(currentMoisture, productionEfficiency)
        newMoisture = max(0, currentMoisture - steamProduced)
        newSteam = currentSteam + steamProduced
        Data.set(moisturePath, newMoisture)
        Data.set(steamPath, newSteam)
        Data.save()
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ProcessSteamConsumption(steamerKey):
    """处理蒸汽消耗"""
    try:
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentSteam = Data.getInt(steamPath, 0)
        if currentSteam <= 0:
            return False
        consumptionEfficiency = Config.getInt("Setting.Steamer.SteamConsumptionEfficiency", 1)
        totalConsumption = consumptionEfficiency
        newSteam = max(0, currentSteam - totalConsumption)
        Data.set(steamPath, newSteam)
        Data.save()
        return newSteam > 0
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def GiveItemToPlayer(Player, Item):
    """给予玩家物品，处理背包空间不足的情况"""
    if not Player or not Item:
        return
    if Player.getInventory().firstEmpty() != -1:
        Player.getInventory().addItem(Item)
    else:
        dropLocation = Player.getLocation()
        ItemEntity = Player.getWorld().dropItemNaturally(dropLocation, Item)
        ItemEntity.setPickupDelay(0)

def RemoveItemToPlayer(Player, Item):
    """移除玩家物品"""
    if not Player or not Item or Item.getType() == Material.AIR:
        return
    if Item.getAmount() > 1:
        newItem = Item.clone()
        newItem.setAmount(Item.getAmount() - 1)
        Player.getInventory().setItemInMainHand(newItem)
    else:
        Player.getInventory().setItemInMainHand(None)

def CreateItemDisplay(Location, Item, Target):
    """创建物品展示实体并设置属性

    参数:
        Location: 生成位置
        Item: 展示的物品
        Target: 目标
    返回:
        创建的展示实体
    """
    ItemDisplayEntity = Location.getWorld().spawn(Location, ItemDisplay)
    DisplayItem = Item.clone()
    DisplayItem.setAmount(1)
    ItemDisplayEntity.setItemStack(DisplayItem)
    ItemIdentifier = ToolUtils.getItemIdentifier(Item)
    ConfigKey = "Setting." + Target + ".DisplayEntity." + ItemIdentifier
    if not Config.contains(ConfigKey + ".Scale"):
        Type = ToolUtils.isBlockMaterialType(Item)
        ConfigKey = "Setting." + Target + ".DisplayEntity." + Type
    Scale = Config.getDouble(ConfigKey + ".Scale")
    ScaleVector = Vector3f(Scale, Scale, Scale)
    RotX = Config.getDouble(ConfigKey + ".Rotation.X")
    RotY = Config.getDouble(ConfigKey + ".Rotation.Y")
    RotZConfig = Config.get(ConfigKey + ".Rotation.Z")
    RotZ = 0.0
    if isinstance(RotZConfig, basestring):  # type: ignore
        if "-" in RotZConfig:
            try:
                MinValue, MaxValue = map(float, RotZConfig.split("-"))
                RotZ = random.uniform(MinValue, MaxValue)
            except ValueError: 
                RotZ = 0.0
        else:
            try: 
                RotZ = float(RotZConfig)
            except ValueError: 
                RotZ = 0.0
    else:
        try: 
            RotZ = float(RotZConfig)
        except ValueError: 
            RotZ = 0.0
    RadX = math.radians(RotX)
    RadY = math.radians(RotY)
    RadZ = math.radians(RotZ)
    Rotation = Quaternionf().rotationXYZ(RadX, RadY, RadZ)
    New_Transform = Transformation(
        Vector3f(),
        Rotation,
        ScaleVector,
        Quaternionf())
    ItemDisplayEntity.setTransformation(New_Transform)
    ItemDisplayEntity.setInvulnerable(True)
    ItemDisplayEntity.setSilent(True)
    ItemDisplayEntity.setPersistent(True)
    ItemDisplayEntity.setGravity(False)
    ItemDisplayEntity.setCustomNameVisible(False)
    return ItemDisplayEntity

def FindNearbyDisplay(Location):
    """在指定位置附近查找物品展示实体

    参数
        Location: 查找位置
    返回
        找到的物品展示实体或None
    """
    FoundEntities = []
    Radius = Config.getDouble("Setting.General.SearchRadius")
    for entity in Location.getWorld().getNearbyEntities(Location, Radius, Radius, Radius):
        if entity.getType() == EntityType.ITEM_DISPLAY: FoundEntities.append(entity)
    return FoundEntities if FoundEntities else None

def GetFileKey(Block):
    """获取砧板的数据文件键

    参数
        Block: 砧板方块
    返回
        str: 数据文件键
    """
    return "{},{},{},{}".format(Block.getX(), Block.getY(), Block.getZ(), Block.getWorld().getName())

def CalculateDisplayLocation(Block, Target, Item=None, ExtraOffset=0):
    """计算物品展示实体的位置

    参数
        Block: 基础方块
        Target: 配方目标
        Item: 物品ItemStack
        ExtraOffset: 额外偏移量
    返回
        展示实体的位置对象
    """
    if Item:
        ItemIdentifier = ToolUtils.getItemIdentifier(Item)
        ConfigKey = "Setting." + Target + ".DisplayEntity." + ItemIdentifier
    else:
        ConfigKey = "Setting." + Target + ".DisplayEntity.Item"
    if not Config.contains(ConfigKey + ".Offset.X"):
        Type = ToolUtils.isBlockMaterialType(Item) if Item else "Item"
        ConfigKey = "Setting." + Target + ".DisplayEntity." + Type
    Offset_X = Config.getDouble(ConfigKey + ".Offset.X")
    Offset_Y = Config.getDouble(ConfigKey + ".Offset.Y")
    Offset_Z = Config.getDouble(ConfigKey + ".Offset.Z")
    return Location(
        Block.getWorld(),
        Block.getX() + Offset_X,
        Block.getY() + Offset_Y + ExtraOffset,
        Block.getZ() + Offset_Z)

ps.listener.registerListener(InteractionVanillaBlock, PlayerInteractEvent)
ps.listener.registerListener(BreakVanillaBlock, BlockBreakEvent)

def CommandExecute(sender, label, args):
    """处理命令

    参数
        sender: 命令发送者
        label: 命令标签
        args: 命令参数
    返回
        bool: 命令执行结果
    """
    if len(args) == 0: return False
    if args[0] == "reload":
        if isinstance(sender, Player):
            if not sender.hasPermission("jiuwukitchen.command.reload"):
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        ReloadPlugin(sender)
        MiniMessageUtils.sendMessage(sender, Config.getString("Messages.Reload.LoadPlugin"), {"Prefix": Prefix})
        return True
    if isinstance(sender, Player):
        if args[0] == "clear":
            if sender.hasPermission("jiuwukitchen.command.clear"):
                for Entity in sender.getWorld().getNearbyEntities(sender.getLocation(), 0.5, 0.5, 0.5):
                    if Entity.getType() == EntityType.ITEM_DISPLAY:
                        Entity.remove()
                        return True
            else:
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        if args[0] == "hand":
            if sender.hasPermission("jiuwukitchen.command.hand"):
                HandItem = sender.getInventory().getItemInMainHand()
                if HandItem.getType() == Material.AIR:
                    MiniMessageUtils.sendMessage(sender, u"&7你手上没有物品")
                    return True
                ItemDisplay = HandItem.displayName()
                ItemDisplay.hoverEvent(HandItem.asHoverEvent())
                MiniMessageUtils.sendMessage(sender, ItemDisplay)
                return True
            else:
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        return False
    return False

def ReloadPlugin(Target = Console):
    global Config, Prefix, ChoppingBoardRecipe, WokRecipe, Data, GrinderRecipe
    ConfigManager.reloadAll()
    Config = ConfigManager.getConfig()
    Prefix = ConfigManager.getPrefix()
    ChoppingBoardRecipe = ConfigManager.getChoppingBoardRecipe()
    WokRecipe = ConfigManager.getWokRecipe()
    GrinderRecipe = ConfigManager.getGrinderRecipe()
    SteamerRecipe = ConfigManager.getSteamerRecipe()
    Data = ConfigManager.getData()
    ChoppingBoardRecipeAmount = ChoppingBoardRecipe.getKeys(False).size()
    WokRecipeAmount = WokRecipe.getKeys(False).size()
    GrinderRecipeAmount = GrinderRecipe.getKeys(False).size()
    SteamerRecipeAmount = SteamerRecipe.getKeys(False).size()
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadChoppingBoardRecipe"),
                                 {"Prefix": Prefix, "Amount": int(ChoppingBoardRecipeAmount)})
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadWokRecipe"),
                                 {"Prefix": Prefix, "Amount": int(WokRecipeAmount)})
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadGrinderRecipe"),
                                 {"Prefix": Prefix, "Amount": int(GrinderRecipeAmount)})
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadSteamerRecipe"),
                                 {"Prefix": Prefix, "Amount": int(SteamerRecipeAmount)})

def TabCommandExecute(sender, label, args):
    """提供命令的补全建议

    参数
        sender: 命令发送者
        label: 命令标签
        args: 命令参数
    返回
        list: 补全建议
    """
    if isinstance(sender, Player):
        return ["reload", "clear", "hand"]
    return ["reload"]

ps.command.registerCommand(CommandExecute, TabCommandExecute, "jiuwukitchen", ["jk"], "")

# 脚本启动检查
def InitializePlugin():
    """插件初始化函数"""
    global PlaceholderAPIAvailable
    ServerPluginLoad()
    if not PlaceholderAPIAvailable:
        if not PlaceholderAPIAvailable:
            MiniMessageUtils.sendMessage(Console, u"{Prefix} <red>服务器未安装 PlaceholderAPI 插件!", {"Prefix": Prefix})
        MiniMessageUtils.sendMessage(Console, u"{Prefix} <red>启动 JiuWu's Kitchen 失败", {"Prefix": Prefix})
        return False
    steamerSection = Data.getConfigurationSection("Steamer")
    if steamerSection:
        steamerKeys = steamerSection.getKeys(False)
        currentTime = System.currentTimeMillis()
        for steamerKey in steamerKeys:
            coolingTime = Data.getLong("Steamer." + steamerKey + ".CoolingTime", 0)
            moisture = Data.getInt("Steamer." + steamerKey + ".Moisture", 0)
            steam = Data.getInt("Steamer." + steamerKey + ".Steam", 0)
            if (coolingTime > currentTime) or (moisture > 0) or (steam > 0):
                StartSteamerTimer()
                break
    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Load"), {"Version": "v1.3.3", "Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console, u"{Prefix} <red>Discord: <gray>https://discord.gg/v39k5Vvzgb", {"Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console, u"{Prefix} <red>QQ群: <gray>299852340", {"Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console, u"{Prefix} <red>Wiki: <gray>https://github.com/jiuwu02/JiuWu-s_Kitchen/wiki", {"Prefix": Prefix})
    ReloadPlugin()
    return True

PluginInitialization = InitializePlugin()

if not PluginInitialization:
    ps.script.unloadScript("JiuWu's_Kitchen.py")