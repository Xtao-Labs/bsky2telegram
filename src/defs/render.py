from typing import TYPE_CHECKING, Optional, Union, List

from datetime import datetime

import pytz
from pydantic import BaseModel

from atproto_client.models.app.bsky.embed.images import View as BskyViewImage
from atproto_client.models.app.bsky.embed.video import View as BskyViewVideo
from atproto_client.models.app.bsky.embed.external import View as BskyViewExternal
from atproto_client.models.app.bsky.embed.record import (
    View as BskyViewRecord,
    ViewRecord as BskyViewRecordRecord,
)

from .bsky_richtext import bsky_html_parser

if TYPE_CHECKING:
    from atproto_client.models.app.bsky.feed.defs import (
        FeedViewPost,
        PostView,
        ThreadViewPost,
    )
    from atproto_client.models.app.bsky.actor.defs import (
        ProfileViewBasic,
        ProfileViewDetailed,
    )

TZ = pytz.timezone("Asia/Shanghai")
XRPC_DOMAIN = "bsky.social"
LABELERS = ["did:plc:ar7c4by46qjdydhdevvrndac"]


class HumanAuthor(BaseModel):
    display_name: str
    handle: str
    did: str
    avatar_img: Optional[str] = None
    created_at: datetime

    description: Optional[str] = None
    followers_count: Optional[int] = None
    follows_count: Optional[int] = None
    posts_count: Optional[int] = None

    @property
    def url(self) -> str:
        return f"https://bsky.app/profile/{self.handle}"

    @property
    def format(self) -> str:
        return f'<a href="{self.url}">{self.display_name}</a>'

    @property
    def format_handle(self) -> str:
        return f'<a href="{self.url}">@{self.handle}</a>'

    @property
    def time_str(self) -> str:
        # utc+8
        return self.created_at.astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def parse(author: "ProfileViewBasic") -> "HumanAuthor":
        return HumanAuthor(
            display_name=author.display_name or author.handle,
            handle=author.handle,
            did=author.did,
            avatar_img=author.avatar,
            created_at=author.created_at,
        )

    @staticmethod
    def parse_detail(author: "ProfileViewDetailed") -> "HumanAuthor":
        return HumanAuthor(
            display_name=author.display_name or author.handle,
            handle=author.handle,
            did=author.did,
            avatar_img=author.avatar,
            created_at=author.created_at,
            description=author.description,
            followers_count=author.followers_count,
            follows_count=author.follows_count,
            posts_count=author.posts_count,
        )


class HumanRepostInfo(BaseModel):
    by: HumanAuthor
    at: datetime

    @property
    def time_str(self) -> str:
        # utc+8
        return self.at.astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S")


class HumanPost(BaseModel, frozen=False):
    cid: str
    content: str
    images: Optional[list[str]] = None
    gif: Optional[str] = None
    video: Optional[str] = None
    video_thumbnail: Optional[str] = None
    external: Optional[str] = None
    created_at: datetime

    like_count: int
    quote_count: int
    reply_count: int
    repost_count: int

    uri: str

    author: HumanAuthor

    labels: List[str]

    is_quote: bool = False
    is_reply: bool = False
    is_repost: bool = False

    repost_info: Optional[HumanRepostInfo] = None
    parent_post: Optional["HumanPost"] = None

    @property
    def url(self) -> str:
        return self.author.url + "/post/" + self.uri.split("/")[-1]

    @property
    def time_str(self) -> str:
        # utc+8
        return self.created_at.astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def status(self) -> str:
        if self.is_quote:
            return "引用"
        elif self.is_reply:
            return "回复"
        return "发表"

    @property
    def need_spoiler(self) -> bool:
        return any(
            label in ["porn", "sexual", "graphic-media", "nudity"]
            for label in self.labels
        )

    @staticmethod
    def parse_labels(
        post: Union["PostView", "BskyViewRecordRecord"], author: HumanAuthor
    ) -> List[str]:
        labels = []
        if not post.labels:
            return labels
        labelers = LABELERS.copy()
        labelers.append(author.did)
        for label in post.labels:
            if label.src in labelers:
                labels.append(label.val)
        return labels

    @staticmethod
    def parse_view(post: Union["PostView", "BskyViewRecordRecord"]) -> "HumanPost":
        record = post.value if isinstance(post, BskyViewRecordRecord) else post.record
        # author
        author = HumanAuthor.parse(post.author)
        labels = HumanPost.parse_labels(post, author)
        embed = (
            (post.embeds[0] if post.embeds else None)
            if isinstance(post, BskyViewRecordRecord)
            else post.embed
        )
        content = (
            bsky_html_parser.unparse(record.text, record.facets)
            if record.facets
            else record.text
        )
        created_at = record.created_at
        # images
        images = []
        if isinstance(embed, BskyViewImage):
            for image in embed.images:
                images.append(image.fullsize)
        # video
        video, video_thumbnail = None, None
        if isinstance(embed, BskyViewVideo):
            video = f"https://{XRPC_DOMAIN}/xrpc/com.atproto.sync.getBlob?did={author.did}&cid={embed.cid}"
            video_thumbnail = embed.thumbnail
        # gif
        gif, extra = None, None
        if isinstance(embed, BskyViewExternal):
            uri = embed.external.uri
            if ".gif" in uri:
                gif = uri
            else:
                extra = uri
        return HumanPost(
            cid=post.cid,
            content=content,
            images=images,
            gif=gif,
            video=video,
            video_thumbnail=video_thumbnail,
            external=extra,
            created_at=created_at,
            like_count=post.like_count,
            quote_count=post.quote_count,
            reply_count=post.reply_count,
            repost_count=post.repost_count,
            uri=post.uri,
            author=author,
            labels=labels,
        )

    @staticmethod
    def parse(data: "FeedViewPost") -> "HumanPost":
        base = HumanPost.parse_view(data.post)
        is_quote, is_reply, is_repost = False, False, False
        parent_post, repost_info = None, None
        if data.reply:
            is_reply = True
            if hasattr(data.reply.parent, "record"):
                parent_post = HumanPost.parse_view(data.reply.parent)
        elif data.reason:
            is_repost = True
            repost_info = HumanRepostInfo(
                by=HumanAuthor.parse(data.reason.by),
                at=data.reason.indexed_at,
            )
        elif data.post.embed and isinstance(data.post.embed, BskyViewRecord):
            is_quote = True
            if isinstance(data.post.embed.record, BskyViewRecordRecord):
                parent_post = HumanPost.parse_view(data.post.embed.record)
        base.is_quote = is_quote
        base.is_reply = is_reply
        base.is_repost = is_repost
        base.parent_post = parent_post
        base.repost_info = repost_info
        return base

    @staticmethod
    def parse_thread(data: "ThreadViewPost") -> "HumanPost":
        base = HumanPost.parse_view(data.post)
        is_quote, is_reply, is_repost = False, False, False
        parent_post = None
        if data.parent:
            is_reply = True
            if hasattr(data.parent, "post"):
                parent_post = HumanPost.parse_thread(data.parent)
        elif data.post.embed and isinstance(data.post.embed, BskyViewRecord):
            is_quote = True
            if isinstance(data.post.embed.record, BskyViewRecordRecord):
                parent_post = HumanPost.parse_view(data.post.embed.record)
        base.is_quote = is_quote
        base.is_reply = is_reply
        base.is_repost = is_repost
        base.parent_post = parent_post
        return base
