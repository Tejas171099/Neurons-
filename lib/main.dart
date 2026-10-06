import 'package:flutter/material.dart';

void main() {
  runApp(const SafetyApp());
}

class SafetyApp extends StatelessWidget {
  const SafetyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Gmail',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const InboxScreen(),
    );
  }
}

class EmailItem {
  final String senderName;
  final String displayedEmail;
  final String actualEmail;
  final String subject;
  final String snippet;
  final String body;
  final int safetyScore;
  final String riskLevel;
  final Color riskColor;
  final String threatReason;
  final String time;
  final String attachmentName;
  final String attachmentStatus;

  const EmailItem({
    required this.senderName,
    required this.displayedEmail,
    required this.actualEmail,
    required this.subject,
    required this.snippet,
    required this.body,
    required this.safetyScore,
    required this.riskLevel,
    required this.riskColor,
    required this.threatReason,
    required this.time,
    required this.attachmentName,
    required this.attachmentStatus,
  });
}

class InboxScreen extends StatelessWidget {
  const InboxScreen({super.key});

  static const List<EmailItem> dummyEmails = [
    EmailItem(
      senderName: 'HDFC Bank Alerts',
      displayedEmail: 'HDFC Bank Alerts',
      actualEmail: 'support@hdfc-verification-desk.net',
      subject: 'Urgent: Your HDFC NetBanking Account will be suspended in 24 Hours!',
      snippet: 'Dear Customer, your account requires immediate verification due to unusual activity...',
      body: 'Dear Customer,\n\nYour HDFC NetBanking Account will be suspended within 24 hours due to suspicious login attempts. Please click the attached secure form and verify your credentials immediately to avoid permanent deactivation.\n\nRegards,\nHDFC Security Team',
      safetyScore: 12,
      riskLevel: 'CRITICAL RISK',
      riskColor: Colors.red,
      threatReason: 'Domain Mismatch: Official domain is hdfcbank.com, but sender uses hdfc-verification-desk.net. Linguistic urgency detected.',
      time: '7:34 PM',
      attachmentName: 'Invoice_Form.pdf',
      attachmentStatus: 'Blocked: Zero-Day Credential Form Detected',
    ),
    EmailItem(
      senderName: 'Netflix Billing',
      displayedEmail: 'Netflix Support',
      actualEmail: 'billing@net-flix-updates-2026.com',
      subject: 'Action Required: Update your payment method',
      snippet: 'We were unable to process your latest monthly subscription payment...',
      body: 'Hi, \n\nWe were unable to process your latest subscription fee. Please update your billing details using the link below to continue streaming without interruption.\n\nThank you,\nNetflix Team',
      safetyScore: 55,
      riskLevel: 'SUSPICIOUS / UNVERIFIED',
      riskColor: Colors.orange,
      threatReason: 'Recently registered domain (less than 14 days old). Sender address does not match verified netflix.com SPF records.',
      time: '6:15 PM',
      attachmentName: 'Billing_Details.html',
      attachmentStatus: 'Warning: Contains external script links',
    ),
    EmailItem(
      senderName: 'DigiLocker',
      displayedEmail: 'DigiLocker Govt',
      actualEmail: 'no-reply@digilocker.gov.in',
      subject: 'Aadhaar KYC Successfully Completed',
      snippet: 'Dear User, We are pleased to inform you that your Aadhaar details have...',
      body: 'Dear User,\n\nYour Aadhaar KYC has been successfully verified and updated in your DigiLocker account. You can now access your official digital documents anytime.\n\nRegards,\nDigiLocker Team',
      safetyScore: 99,
      riskLevel: 'SAFE',
      riskColor: Colors.green,
      threatReason: 'Verified Govt Domain (.gov.in). Valid DKIM and SPF signature records found.',
      time: '4:20 PM',
      attachmentName: 'None',
      attachmentStatus: 'Clean',
    ),
    EmailItem(
      senderName: 'HackerRank Team',
      displayedEmail: 'HackerRank',
      actualEmail: 'events@hackerrank.com',
      subject: 'You have registered for Orchestrate Oct 2026',
      snippet: 'HackerRank Hey Aastha, You have successfully registered for the upcoming...',
      body: 'Hi Aastha,\n\nYou have successfully registered for Orchestrate Oct 2026 coding challenge. Make sure to check your calendar and test your system requirements prior to the event.\n\nBest,HackerRank Team',
      safetyScore: 95,
      riskLevel: 'SAFE',
      riskColor: Colors.green,
      threatReason: 'Legitimate corporate domain matching hackerrank.com email infrastructure.',
      time: '2:10 PM',
      attachmentName: 'None',
      attachmentStatus: 'Clean',
    ),
    EmailItem(
      senderName: 'Amazon Security',
      displayedEmail: 'Amazon Prime Services',
      actualEmail: 'secure-login@amazon-prime-update-in.com',
      subject: 'Your Prime Membership is expiring today! Claim refund',
      snippet: 'Click here to update your credit card info to prevent membership cancellation...',
      body: 'Dear Member, your Amazon Prime subscription payment failed. Click the link below to update billing information or lose your benefits immediately.\n\nThanks,\nAmazon Support',
      safetyScore: 20,
      riskLevel: 'CRITICAL RISK',
      riskColor: Colors.red,
      threatReason: 'Lookalike domain spoofing. Official domain is amazon.in / amazon.com.',
      time: '11:05 AM',
      attachmentName: 'Claim_Form.html',
      attachmentStatus: 'Malicious Script Found',
    ),
    EmailItem(
      senderName: 'Zomato Support',
      displayedEmail: 'Zomato Helpdesk',
      actualEmail: 'order-update@zomato-support-refund.net',
      subject: 'Refund Issued: ₹450 for Cancelled Order #9821',
      snippet: 'Your order was cancelled. Click the secure link to claim your instant wallet refund...',
      body: 'Dear Customer, we have processed a refund for your cancelled order. Please submit your UPI PIN and bank account details via the attached form to credit the amount instantly.',
      safetyScore: 18,
      riskLevel: 'CRITICAL RISK',
      riskColor: Colors.red,
      threatReason: 'Phishing attempt via fake credential harvesting form targeting financial details.',
      time: '9:40 AM',
      attachmentName: 'Claim_Refund.pdf',
      attachmentStatus: 'Malicious Payload Detected',
    ),
    EmailItem(
      senderName: 'GitHub Community',
      displayedEmail: 'GitHub',
      actualEmail: 'no-reply@github.com',
      subject: 'Security Alert: New personal access token created',
      snippet: 'A personal access token (repo_scope) was recently added to your account...',
      body: 'Hi Aastha,\n\nA new personal access token was created for your GitHub account from a Linux machine in Bangalore. If you initiated this, no action is needed.\n\nRegards,\nGitHub Security',
      safetyScore: 92,
      riskLevel: 'SAFE',
      riskColor: Colors.green,
      threatReason: 'Valid DKIM signature verified from official github.com domain infrastructure.',
      time: 'Yesterday',
      attachmentName: 'None',
      attachmentStatus: 'Clean',
    ),
    EmailItem(
      senderName: 'ICICI Bank Support',
      displayedEmail: 'ICICI Bank Alerts',
      actualEmail: 'alert@icici-secure-netbanking-update.com',
      subject: 'Debit Card Blocked! Update KYC immediately',
      snippet: 'Your ICICI debit card has been temporarily blocked due to security reasons...',
      body: 'Dear User,\n\nYour ICICI Bank Debit Card has been blocked. Please click the link below to update your PAN and Aadhaar details to unblock it instantly.\n\nRegards,\nICICI Team',
      safetyScore: 15,
      riskLevel: 'CRITICAL RISK',
      riskColor: Colors.red,
      threatReason: 'Phishing domain spoofing bank portal. Credential harvesting detected.',
      time: 'Yesterday',
      attachmentName: 'KYC_Form.html',
      attachmentStatus: 'Malicious Script Found',
    ),
    EmailItem(
      senderName: 'Swiggy Instamart',
      displayedEmail: 'Swiggy Offers',
      actualEmail: 'offers@swiggy.in',
      subject: 'You won a ₹200 Cashback on your next order!',
      snippet: 'Congratulations Aastha! Use code INSTA200 to claim your reward on groceries...',
      body: 'Hi Aastha,\n\nThank you for being a loyal Swiggy Instamart customer. Enjoy ₹200 off on your next grocery order above ₹500 using your app.\n\nHappy Shopping,\nSwiggy Team',
      safetyScore: 94,
      riskLevel: 'SAFE',
      riskColor: Colors.green,
      threatReason: 'Verified domain infrastructure matching official swiggy.in records.',
      time: 'Oct 4',
      attachmentName: 'None',
      attachmentStatus: 'Clean',
    ),
    EmailItem(
      senderName: 'Income Tax Department',
      displayedEmail: 'Income Tax India',
      actualEmail: 'refund-portal@incometax-gov-in-update.net',
      subject: 'Approved: Your Tax Refund of ₹12,450 is ready',
      snippet: 'Click here to validate your bank account number and claim your tax refund...',
      body: 'Dear Taxpayer,\n\nYour annual tax assessment is complete. An amount of ₹12,450 is pending transfer. Verify your account details immediately via the secure link.\n\nIncome Tax Dept',
      safetyScore: 10,
      riskLevel: 'CRITICAL RISK',
      riskColor: Colors.red,
      threatReason: 'Severe spoofing of government domain (.gov.in simulated via malicious external link).',
      time: 'Oct 3',
      attachmentName: 'Refund_Form.pdf',
      attachmentStatus: 'Dangerous Executable',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                height: 48,
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(color: Colors.grey.withValues(alpha: 0.2), blurRadius: 4, offset: const Offset(0, 2)),
                  ],
                ),
                child: Row(
                  children: [
                    const Icon(Icons.menu, color: Colors.black54),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text('Search in mail', style: TextStyle(color: Colors.grey.shade600, fontSize: 16)),
                    ),
                    const CircleAvatar(
                      radius: 16,
                      backgroundColor: Colors.pink,
                      child: Text('A', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text('Primary', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
              ),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: dummyEmails.length,
                itemBuilder: (context, index) {
                  final email = dummyEmails[index];
                  return InkWell(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => EmailDetailScreen(email: email),
                        ),
                      );
                    },
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          CircleAvatar(
                            backgroundColor: email.riskColor.withValues(alpha: 0.2),
                            child: Text(
                              email.senderName[0],
                              style: TextStyle(color: email.riskColor, fontWeight: FontWeight.bold),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      email.senderName,
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                                    ),
                                    Text(
                                      email.time,
                                      style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  email.subject,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  email.snippet,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          Column(
                            children: [
                              const Icon(Icons.star_border, size: 20, color: Colors.grey),
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: email.riskColor.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: email.riskColor),
                                ),
                                child: Text(
                                  '${email.safetyScore}',
                                  style: TextStyle(color: email.riskColor, fontWeight: FontWeight.bold, fontSize: 11),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class EmailDetailScreen extends StatelessWidget {
  final EmailItem email;

  const EmailDetailScreen({super.key, required this.email});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black87),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(icon: const Icon(Icons.archive_outlined, color: Colors.black87), onPressed: () {}),
          IconButton(icon: const Icon(Icons.delete_outline, color: Colors.black87), onPressed: () {}),
          IconButton(icon: const Icon(Icons.mail_outline, color: Colors.black87), onPressed: () {}),
          const SizedBox(width: 8),
          const Icon(Icons.more_vert, color: Colors.black87),
          const SizedBox(width: 12),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              email.subject,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black87),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text('Inbox', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    flex: 4,
                    child: Card(
                      elevation: 2,
                      color: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: BorderSide(color: Colors.grey.shade300, width: 1),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(10.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text('Safety Score', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 6),
                            Stack(
                              alignment: Alignment.center,
                              children: [
                                SizedBox(
                                  height: 54,
                                  width: 54,
                                  child: CircularProgressIndicator(
                                    value: email.safetyScore / 100,
                                    strokeWidth: 6,
                                    backgroundColor: Colors.grey.shade200,
                                    color: email.riskColor,
                                  ),
                                ),
                                Text('${email.safetyScore}/100', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: email.riskColor)),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              email.riskLevel, 
                              style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: email.riskColor),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 6,
                    child: Card(
                      elevation: 2,
                      color: Colors.white,
                      shape: RoundedRectangleBorder(
                        side: BorderSide(color: email.riskColor, width: 1.5),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(10.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.warning_amber_rounded, color: email.riskColor, size: 18),
                                const SizedBox(width: 4),
                                Text('Sender Check', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: email.riskColor)),
                              ],
                            ),
                            const Divider(height: 8),
                            Text('Display: "${email.displayedEmail}"', style: const TextStyle(fontSize: 10, color: Colors.black87), maxLines: 1, overflow: TextOverflow.ellipsis),
                            const SizedBox(height: 3),
                            Text(
                              'Actual: ${email.actualEmail}',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: email.safetyScore < 40 ? Colors.red.shade800 : (email.safetyScore < 70 ? Colors.orange.shade900 : Colors.green.shade700),
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            if (email.attachmentName != 'None') ...[
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.insert_drive_file, color: Colors.red, size: 28),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(email.attachmentName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                          Text(email.attachmentStatus, style: TextStyle(color: email.riskColor, fontSize: 11)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            Text(
              email.body,
              style: const TextStyle(fontSize: 14, height: 1.5, color: Colors.black87),
            ),
            const SizedBox(height: 20),

            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('AI Threat Analysis', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
                  const SizedBox(height: 4),
                  Text(email.threatReason, style: TextStyle(fontSize: 12, color: Colors.grey.shade800)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.shade700,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 2),
                      textStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {},
                    icon: const Icon(Icons.block, size: 12),
                    label: const Text('Block Sender', textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis),
                  ),
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange.shade800,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 2),
                      textStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {},
                    icon: const Icon(Icons.report, size: 12),
                    label: const Text('Report Cyber Fraud', textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis),
                  ),
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green.shade700,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 2),
                      textStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {},
                    icon: const Icon(Icons.check_circle, size: 12),
                    label: const Text('Mark Safe', textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}