db.forum.insertMany([
  {
    content: "Long content",
    replies: [
      {
        id: 1,
        content: "Reply content 1",
        replies: [
          {
            id: 2,
            content: "Reply content 2",
            replies: [],
          },
          {
            id: 3,
            content: "Reply content 3",
            replies: [
              {
                id: 4,
                content: "Reply content 4",
                replies: [],
              },
            ],
          },
        ],
      },
      {
        id: 5,
        content: "Reply content 5",
        replies: [
          {
            id: 6,
            content: "Reply content 6",
            replies: [],
          },
        ],
      },
    ],
  },
  {
    content: "Long content",
    replies: [
      {
        id: 7,
        content: "Reply content 7",
        replies: [
          {
            id: 8,
            content: "Reply content 8",
            replies: [],
          },
          {
            id: 9,
            content: "Reply content 9",
            replies: [
              {
                id: 10,
                content: "Reply content 10",
                replies: [],
              },
            ],
          },
        ],
      },
      {
        id: 11,
        content: "Reply content 11",
        replies: [
          {
            id: 12,
            content: "Reply content 12",
            replies: [],
          },
        ],
      },
    ],
  },
]);

// Second level update
db.forum.update(
  { _id: ObjectId("6203698e4e8a0f76367f555f"), "replies.id": 1 },
  {
    $push: {
      "replies.$[].replies": {
        id: 13,
        content: "Reply content 13",
        replies: [],
      },
    },
  }
);
// Third level update
db.forum.update(
  { _id: ObjectId("6203698e4e8a0f76367f555f"), "replies.replies.id": 2 },
  {
    $push: {
      "replies.$[].replies.$[].replies": {
        id: 14,
        content: "Reply content 14",
        replies: [],
      },
    },
  }
);

// Extract data
db.forum.aggregate([
  {
    $project: {
      replies: {
        $filter: {
          input: "$replies",
          as: "reply",
          $cond: { $eq: ["$$reply.id", 2] },
        },
      },
    },
  },
]);
