import unittest
from unittest.mock import patch, Mock
from lk_compat_helper.commit_to_tag import CLinuxKernelRepo
import github


# Mock out server communication
@patch("github.Github", Mock())
@patch("github.Github.get_repo", Mock())
class CLinuxKernelRepoUnitTest(unittest.TestCase):
    def setUp(self):
        pass

    def _get_commit_obj(self, sha, date):
        return github.Commit.Commit(
            requester=None,
            headers={},
            attributes={
                "commit": {
                    "sha": sha,
                    "committer": {"name": "tkc", "date": date},
                }
            },
            completed=True,
        )

    def _get_tag_objs(self, tags):
        return [
            github.Tag.Tag(
                requester=None,
                headers={},
                attributes={
                    "name": tag,
                    "commit": {
                        "commit": {
                            "sha": sha,
                            "committer": {"name": "tkc", "date": date},
                        }
                    },
                },
                completed=True,
            )
            for tag, sha, date in tags
        ]

    @patch("lk_compat_helper.commit_to_tag.CLinuxKernelRepo._get_tags")
    @patch("lk_compat_helper.commit_to_tag.CLinuxKernelRepo._get_commit")
    def test_empty_tags(self, mock_get_commit, mock_get_tags):
        commit = "1e28eed17697"
        exp_tag = "Unknown"
        commit_date = "2021-03-13T08:33:34Z"
        mock_get_commit.return_value = self._get_commit_obj(commit, commit_date)
        mock_get_tags.return_value = ([], 0)
        lk_repo = CLinuxKernelRepo(None, commit)
        self.assertEqual(lk_repo.get_tag(), exp_tag)

    @patch("sys.exit", Mock())
    @patch("lk_compat_helper.commit_to_tag.CLinuxKernelRepo._get_tags")
    @patch("lk_compat_helper.commit_to_tag.CLinuxKernelRepo._get_commit")
    def test_empty_commit_date(self, mock_get_commit, mock_get_tags):
        commit = "1e28eed17697"
        exp_tag = "Unknown"
        commit_date = None
        mock_get_commit.return_value = self._get_commit_obj(commit, commit_date)
        mock_get_tags.return_value = ([], 0)
        lk_repo = CLinuxKernelRepo(None, commit)
        self.assertEqual(lk_repo.get_tag(), exp_tag)

    @patch("lk_compat_helper.commit_to_tag.CLinuxKernelRepo._get_tags")
    @patch("lk_compat_helper.commit_to_tag.CLinuxKernelRepo._get_commit")
    def _setup_and_run_test(
        self,
        commit,
        commit_date,
        exp_tag,
        tags,
        mock_get_commit,
        mock_get_tags,
    ):
        mock_get_commit.reset_mock(return_value=True)
        mock_get_tags.reset_mock(return_value=True)
        mock_get_commit.return_value = self._get_commit_obj(commit, commit_date)
        mock_get_tags.return_value = (self._get_tag_objs(tags), len(tags))
        lk_repo = CLinuxKernelRepo(None, commit)
        self.assertEqual(lk_repo.get_tag(), exp_tag)

    def test_get_tag(self):
        commit = "1e28eed17697"
        exp_tag = "v5.11"
        commit_date = "2021-03-20T08:33:34Z"
        tags = [
            (
                "v5.12",
                "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3",
                "2021-03-28T22:48:16Z",
            ),
            (
                "v5.11",
                "0d02ec6b3136c73c09e7859f0d0e4e2c4c07b49b",
                "2021-03-21T22:48:16Z",
            ),
            (
                "v5.10",
                "1e28eed17697bcf343c6743f0028cc3b5dd88bf0",
                "2021-03-14T22:48:16Z",
            ),
        ]
        self._setup_and_run_test(commit, commit_date, exp_tag, tags)

    def test_get_tag_last(self):
        commit = "1e28eed17697"
        exp_tag = "v5.10"
        commit_date = "2021-03-13T08:33:34Z"
        tags = [
            (
                "v5.12",
                "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3",
                "2021-03-28T22:48:16Z",
            ),
            (
                "v5.11",
                "0d02ec6b3136c73c09e7859f0d0e4e2c4c07b49b",
                "2021-03-21T22:48:16Z",
            ),
            (
                "v5.10",
                "1e28eed17697bcf343c6743f0028cc3b5dd88bf0",
                "2021-03-14T22:48:16Z",
            ),
        ]
        self._setup_and_run_test(commit, commit_date, exp_tag, tags)

    def test_get_tag_last_equal(self):
        commit = "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3"
        exp_tag = "v5.12"
        commit_date = "2021-03-28T22:48:16Z"
        tags = [
            (
                "v5.12",
                "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3",
                "2021-03-28T22:48:16Z",
            ),
            (
                "v5.11",
                "0d02ec6b3136c73c09e7859f0d0e4e2c4c07b49b",
                "2021-03-21T22:48:16Z",
            ),
            (
                "v5.10",
                "1e28eed17697bcf343c6743f0028cc3b5dd88bf0",
                "2021-03-14T22:48:16Z",
            ),
        ]
        self._setup_and_run_test(commit, commit_date, exp_tag, tags)

    def test_get_tag_wrong_sha(self):
        commit = "12345789abc"
        exp_tag = "v5.11"
        commit_date = "2021-03-20T08:33:34Z"
        tags = [
            (
                "v5.12",
                "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3",
                "2021-03-28T22:48:16Z",
            ),
            (
                "v5.11",
                "0d02ec6b3136c73c09e7859f0d0e4e2c4c07b49b",
                "2021-03-21T22:48:16Z",
            ),
            (
                "v5.10",
                "1e28eed17697bcf343c6743f0028cc3b5dd88bf0",
                "2021-03-14T22:48:16Z",
            ),
        ]
        self._setup_and_run_test(commit, commit_date, exp_tag, tags)

    def test_get_tag_wrong_sha_unmerged(self):
        commit = "12345789abc"
        exp_tag = "Unmerged"
        commit_date = "2021-03-29T08:33:34Z"
        tags = [
            (
                "v5.12",
                "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3",
                "2021-03-28T22:48:16Z",
            ),
            (
                "v5.11",
                "0d02ec6b3136c73c09e7859f0d0e4e2c4c07b49b",
                "2021-03-21T22:48:16Z",
            ),
            (
                "v5.10",
                "1e28eed17697bcf343c6743f0028cc3b5dd88bf0",
                "2021-03-14T22:48:16Z",
            ),
        ]
        self._setup_and_run_test(commit, commit_date, exp_tag, tags)

    def test_get_tag_all_rcs(self):
        commit = "12345789abc"
        # Not possible IRL
        exp_tag = "Unknown"
        commit_date = "2021-03-29T08:33:34Z"
        tags = [
            (
                "v5.12-rc",
                "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3",
                "2021-03-28T22:48:16Z",
            ),
            (
                "v5.11-rc-dont-use",
                "0d02ec6b3136c73c09e7859f0d0e4e2c4c07b49b",
                "2021-03-21T22:48:16Z",
            ),
            (
                "v5.10-rc",
                "1e28eed17697bcf343c6743f0028cc3b5dd88bf0",
                "2021-03-14T22:48:16Z",
            ),
        ]
        self._setup_and_run_test(commit, commit_date, exp_tag, tags)

    def test_get_tag_stress(self):
        commit = "50508d941c180a105fdba802d5af1abf3d93a625"
        exp_tag = "v5.3"
        commit_date = "2019-07-31T09:00:46Z"
        tags = [
            (
                "v5.12-rc6",
                "e49d033bddf5b565044e2abe4241353959bc9120",
                "2021-04-04T21:15:36Z",
            ),
            (
                "v5.12-rc5",
                "a5e13c6df0e41702d2b2c77c8ad41677ebb065b3",
                "2021-03-28T22:48:16Z",
            ),
            (
                "v5.12-rc4",
                "0d02ec6b3136c73c09e7859f0d0e4e2c4c07b49b",
                "2021-03-21T21:56:43Z",
            ),
            (
                "v5.12-rc3",
                "1e28eed17697bcf343c6743f0028cc3b5dd88bf0",
                "2021-03-14T21:41:02Z",
            ),
            (
                "v5.12-rc2",
                "a38fd8748464831584a19438cbb3082b5a2dab15",
                "2021-03-06T01:33:41Z",
            ),
            (
                "v5.12-rc1-dontuse",
                "fe07bfda2fb9cdef8a4d4008a409bb02f35f1bd8",
                "2021-03-01T00:05:19Z",
            ),
            (
                "v5.11",
                "f40ddce88593482919761f74910f42f4b84c004b",
                "2021-02-14T22:32:24Z",
            ),
            (
                "v5.11-rc7",
                "92bf22614b21a2706f4993b278017e437f7785b3",
                "2021-02-07T21:57:38Z",
            ),
            (
                "v5.11-rc6",
                "1048ba83fb1c00cd24172e23e8263972f6b5d9ac",
                "2021-01-31T21:50:09Z",
            ),
            (
                "v5.11-rc5",
                "6ee1d745b7c9fd573fba142a2efdad76a9f1cb04",
                "2021-01-25T00:47:14Z",
            ),
            (
                "v5.11-rc4",
                "19c329f6808995b142b3966301f217c831e7cf31",
                "2021-01-18T00:37:05Z",
            ),
            (
                "v5.11-rc3",
                "7c53f6b671f4aba70ff15e1b05148b10d58c2837",
                "2021-01-10T22:34:50Z",
            ),
            (
                "v5.11-rc2",
                "e71ba9452f0b5b2e8dc8aa5445198cd9214a6a62",
                "2021-01-03T23:55:30Z",
            ),
            (
                "v5.11-rc1",
                "5c8fe583cce542aa0b84adc939ce85293de36e5e",
                "2020-12-27T23:30:22Z",
            ),
            (
                "v5.10",
                "2c85ebc57b3e1817b6ce1a6b703928e113a90442",
                "2020-12-13T22:41:30Z",
            ),
            (
                "v5.10-rc7",
                "0477e92881850d44910a7e94fc2c46f96faa131f",
                "2020-12-06T22:25:12Z",
            ),
            (
                "v5.10-rc6",
                "b65054597872ce3aefbc6a666385eabdf9e288da",
                "2020-11-29T23:50:50Z",
            ),
            (
                "v5.10-rc5",
                "418baf2c28f3473039f2f7377760bd8f6897ae18",
                "2020-11-22T23:36:08Z",
            ),
            (
                "v5.10-rc4",
                "09162bc32c880a791c6c0668ce0745cf7958f576",
                "2020-11-16T00:44:31Z",
            ),
            (
                "v5.10-rc3",
                "f8394f232b1eab649ce2df5c5f15b0e528c92091",
                "2020-11-09T00:10:16Z",
            ),
            (
                "v5.10-rc2",
                "3cea11cd5e3b00d91caf0b4730194039b45c5891",
                "2020-11-01T22:43:51Z",
            ),
            (
                "v5.10-rc1",
                "3650b228f83adda7e5ee532e2b90429c03f7b9ec",
                "2020-10-25T22:14:11Z",
            ),
            (
                "v5.9",
                "bbf5c979011a099af5dc76498918ed7df445635b",
                "2020-10-11T21:15:50Z",
            ),
            (
                "v5.9-rc8",
                "549738f15da0e5a00275977623be199fbbf7df50",
                "2020-10-04T23:04:34Z",
            ),
            (
                "v5.9-rc7",
                "a1b8638ba1320e6684aa98233c15255eb803fac7",
                "2020-09-27T21:38:10Z",
            ),
            (
                "v5.9-rc6",
                "ba4f184e126b751d1bffad5897f263108befc780",
                "2020-09-20T23:33:55Z",
            ),
            (
                "v5.9-rc5",
                "856deb866d16e29bd65952e0289066f6078af773",
                "2020-09-13T23:06:00Z",
            ),
            (
                "v5.9-rc4",
                "f4d51dffc6c01a9e94650d95ce0104964f8ae822",
                "2020-09-07T00:11:40Z",
            ),
            (
                "v5.9-rc3",
                "f75aef392f869018f78cfedf3c320a6b3fcfda6b",
                "2020-08-30T23:01:54Z",
            ),
            (
                "v5.9-rc2",
                "d012a7190fc1fd72ed48911e77ca97ba4521bccd",
                "2020-08-23T21:08:43Z",
            ),
            (
                "v5.9-rc1",
                "9123e3a74ec7b934a4a099e98af6a61c2f80bbf5",
                "2020-08-16T20:04:57Z",
            ),
            (
                "v5.8",
                "bcf876870b95592b52519ed4aafcf9d95999bc9c",
                "2020-08-02T21:21:45Z",
            ),
            (
                "v5.8-rc7",
                "92ed301919932f777713b9172e525674157e983d",
                "2020-07-26T21:14:06Z",
            ),
            (
                "v5.8-rc6",
                "ba47d845d715a010f7b51f6f89bae32845e6acb7",
                "2020-07-19T22:41:18Z",
            ),
            (
                "v5.8-rc5",
                "11ba468877bb23f28956a35e896356252d63c983",
                "2020-07-12T23:34:50Z",
            ),
            (
                "v5.8-rc4",
                "dcb7fd82c75ee2d6e6f9d8cc71c52519ed52e258",
                "2020-07-05T23:20:22Z",
            ),
            (
                "v5.8-rc3",
                "9ebcfadb0610322ac537dd7aa5d9cbc2b2894c68",
                "2020-06-28T22:00:24Z",
            ),
            (
                "v5.8-rc2",
                "48778464bb7d346b47157d21ffde2af6b2d39110",
                "2020-06-21T22:45:29Z",
            ),
            (
                "v5.8-rc1",
                "b3a9e3b9622ae10064826dccb4f7a52bd88c7407",
                "2020-06-14T19:45:04Z",
            ),
            (
                "v5.7",
                "3d77e6a8804abcc0504c904bd6e5cdf3a5cf8162",
                "2020-05-31T23:49:15Z",
            ),
            (
                "v5.7-rc7",
                "9cb1fd0efd195590b828b9b865421ad345a4a145",
                "2020-05-24T22:32:54Z",
            ),
            (
                "v5.7-rc6",
                "b9bbe6ed63b2b9f2c9ee5cbd0f2c946a2723f4ce",
                "2020-05-17T23:48:37Z",
            ),
            (
                "v5.7-rc5",
                "2ef96a5bb12be62ef75b5828c0aab838ebb29cb8",
                "2020-05-10T22:16:58Z",
            ),
            (
                "v5.7-rc4",
                "0e698dfa282211e414076f9dc7e83c1c288314fd",
                "2020-05-03T21:56:04Z",
            ),
            (
                "v5.7-rc3",
                "6a8b55ed4056ea5559ebe4f6a4b247f627870d4c",
                "2020-04-26T20:51:02Z",
            ),
            (
                "v5.7-rc2",
                "ae83d0b416db002fe95601e7f97f64b59514d936",
                "2020-04-19T21:35:30Z",
            ),
            (
                "v5.7-rc1",
                "8f3d9f354286745c751374f5f1fcafee6b3f3136",
                "2020-04-12T19:35:55Z",
            ),
            (
                "v5.6",
                "7111951b8d4973bda27ff663f2cf18b663d15b48",
                "2020-03-29T22:25:41Z",
            ),
            (
                "v5.6-rc7",
                "16fbf79b0f83bc752cee8589279f1ebfe57b3b6e",
                "2020-03-23T01:31:56Z",
            ),
            (
                "v5.6-rc6",
                "fb33c6510d5595144d585aa194d377cf74d31911",
                "2020-03-15T22:01:23Z",
            ),
            (
                "v5.6-rc5",
                "2c523b344dfa65a3738e7039832044aa133c75fb",
                "2020-03-09T00:44:44Z",
            ),
            (
                "v5.6-rc4",
                "98d54f81e36ba3bf92172791eba5ca5bd813989b",
                "2020-03-01T22:38:46Z",
            ),
            (
                "v5.6-rc3",
                "f8788d86ab28f61f7b46eb6be375f8a726783636",
                "2020-02-24T00:17:42Z",
            ),
            (
                "v5.6-rc2",
                "11a48a5a18c63fd7621bb050228cebf13566e4d8",
                "2020-02-16T21:16:59Z",
            ),
            (
                "v5.6-rc1",
                "bb6d3fb354c5ee8d6bde2d576eb7220ea09862b9",
                "2020-02-10T00:08:48Z",
            ),
            (
                "v5.5",
                "d5226fa6dbae0569ee43ecfc08bdcd6770fc4755",
                "2020-01-27T00:23:03Z",
            ),
            (
                "v5.5-rc7",
                "def9d2780727cec3313ed3522d0123158d87224d",
                "2020-01-20T00:02:49Z",
            ),
            (
                "v5.5-rc6",
                "b3a987b0264d3ddbb24293ebff10eddfc472f653",
                "2020-01-13T00:55:08Z",
            ),
            (
                "v5.5-rc5",
                "c79f46a282390e0f5b306007bf7b11a46d529538",
                "2020-01-05T22:23:27Z",
            ),
            (
                "v5.5-rc4",
                "fd6988496e79a6a4bdb514a4655d2920209eb85d",
                "2019-12-29T23:29:16Z",
            ),
            (
                "v5.5-rc3",
                "46cf053efec6a3a5f343fead837777efe8252a46",
                "2019-12-23T01:02:23Z",
            ),
            (
                "v5.5-rc2",
                "d1eef1c619749b2a57e514a3fa67d9a516ffa919",
                "2019-12-15T23:16:08Z",
            ),
            (
                "v5.5-rc1",
                "e42617b825f8073569da76dc4510bfa019b1c35a",
                "2019-12-08T22:57:55Z",
            ),
            (
                "v5.4",
                "219d54332a09e8d8741c1e1982f5eae56099de85",
                "2019-11-25T00:32:01Z",
            ),
            (
                "v5.4-rc8",
                "af42d3466bdc8f39806b26f593604fdc54140bcb",
                "2019-11-17T22:47:30Z",
            ),
            (
                "v5.4-rc7",
                "31f4f5b495a62c9a8b15b1c3581acd5efeb9af8c",
                "2019-11-11T00:17:15Z",
            ),
            (
                "v5.4-rc6",
                "a99d8080aaf358d5d23581244e5da23b35e340b9",
                "2019-11-03T22:07:26Z",
            ),
            (
                "v5.4-rc5",
                "d6d5df1db6e9d7f8f76d2911707f7d5877251b02",
                "2019-10-27T17:19:19Z",
            ),
            (
                "v5.4-rc4",
                "7d194c2100ad2a6dded545887d02754948ca5241",
                "2019-10-20T19:56:22Z",
            ),
            (
                "v5.4-rc3",
                "4f5cafb5cb8471e54afdc9054d973535614f7675",
                "2019-10-13T23:37:36Z",
            ),
            (
                "v5.4-rc2",
                "da0c9ea146cbe92b832f1b0f694840ea8eb33cce",
                "2019-10-06T21:27:30Z",
            ),
            (
                "v5.4-rc1",
                "54ecb8f7028c5eb3d740bb82b0f1d90f2df63c5c",
                "2019-09-30T17:35:40Z",
            ),
            (
                "v5.3",
                "4d856f72c10ecb060868ed10ff1b1453943fc6c8",
                "2019-09-15T21:19:32Z",
            ),
            (
                "v5.3-rc8",
                "f74c2bb98776e2de508f4d607cd519873065118e",
                "2019-09-08T20:33:15Z",
            ),
            (
                "v5.3-rc7",
                "089cf7f6ecb266b6a4164919a2e69bd2f938374a",
                "2019-09-02T16:57:40Z",
            ),
            (
                "v5.3-rc6",
                "a55aa89aab90fae7c815b0551b07be37db359d76",
                "2019-08-25T19:01:23Z",
            ),
            (
                "v5.3-rc5",
                "d1abaeb3be7b5fa6d7a1fbbd2e14e3310005c4c1",
                "2019-08-18T21:31:08Z",
            ),
            (
                "v5.3-rc4",
                "d45331b00ddb179e291766617259261c112db872",
                "2019-08-11T20:26:41Z",
            ),
            (
                "v5.3-rc3",
                "e21a712a9685488f5ce80495b37b9fdbe96c230d",
                "2019-08-05T01:40:12Z",
            ),
            (
                "v5.3-rc2",
                "609488bc979f99f805f34e9a32c1e3b71179d10b",
                "2019-07-28T19:47:02Z",
            ),
            (
                "v5.3-rc1",
                "5f9e832c137075045d15cd6899ab0505cfb2ca4b",
                "2019-07-21T21:05:38Z",
            ),
        ]
        self._setup_and_run_test(commit, commit_date, exp_tag, tags)
